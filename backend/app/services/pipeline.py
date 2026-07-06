"""Board analysis pipeline: images → embeddings → board profile → vibe
summary → product candidates → similarity ranking → shoppable results."""

import logging
import re
from typing import Any

import numpy as np

from ..budget import DailyBudget
from ..config import get_settings
from ..storage import Board
from .embeddings import get_embedding_provider
from .embeddings.base import normalize
from .products import Product, get_product_provider
from .vectorstore import get_vector_store
from .vibe import VibeResult, get_vibe_summarizer
from .vibe.stub import StubVibeSummarizer

logger = logging.getLogger("muse.pipeline")

_STOPWORDS = {"the", "a", "an", "and", "with", "in", "of", "for", "to"}

_settings = get_settings()
# Shared across every request in this process: protects the deployment's
# actual Gemini/SerpAPI quota from a traffic spike, independent of the
# per-IP rate limits in routers/boards.py (which only stop one client).
_gemini_budget = DailyBudget("gemini", _settings.gemini_daily_limit)
_serpapi_budget = DailyBudget("serpapi", _settings.serpapi_daily_limit)


def _hex_to_rgb(hex_color: str) -> np.ndarray:
    return np.array(
        [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)], dtype=np.float32
    )


def _palette_affinity(product_color: str, palette: list[str]) -> float:
    """0..1 score: how close the product color sits to the board palette."""
    if not product_color or not palette:
        return 0.5
    rgb = _hex_to_rgb(product_color)
    max_dist = 441.7  # sqrt(3 * 255^2)
    best = min(float(np.linalg.norm(rgb - _hex_to_rgb(c))) for c in palette)
    return 1.0 - best / max_dist


def _why_matched(product: Product, vibe: VibeResult, palette_score: float) -> list[str]:
    reasons: list[str] = []
    text = f"{product.title} {product.details}".lower()
    for tag in vibe.tags:
        words = [w for w in re.split(r"\W+", tag.lower()) if w and w not in _STOPWORDS]
        if words and any(w in text for w in words):
            reasons.append(tag)
        if len(reasons) == 2:
            break
    if palette_score > 0.82:
        reasons.append("palette match")
    if not reasons:
        # Real product titles rarely echo the exact vibe-tag wording, but
        # for API-sourced items we still know which vibe-derived search term
        # surfaced them — a more specific fallback than a generic phrase.
        reasons.append(product.source_query or "overall vibe")
    return reasons[:3]


def _product_text(product: Product) -> str:
    return f"{product.title}. {product.details}. {product.category}"


def _is_gemini(summarizer: object) -> bool:
    from .vibe.gemini import GeminiVibeSummarizer

    return isinstance(summarizer, GeminiVibeSummarizer)


def _rank_and_package(board_id: str, profile: np.ndarray, vibe: VibeResult) -> dict[str, Any]:
    """Shared by analyze_board and refine_board: search products for the
    given vibe's query terms, rank them against the given profile vector,
    and package the shoppable results payload."""
    settings = get_settings()
    embedder = get_embedding_provider()
    store = get_vector_store()
    provider = get_product_provider()
    if provider.name == "serpapi" and not _serpapi_budget.try_consume():
        from .products.mock import MockProductProvider

        logger.warning("SerpAPI daily budget exhausted — serving the mock catalog instead")
        provider = MockProductProvider(settings.api_base_url)

    candidates = provider.search(vibe.query_terms)
    by_id = {p.id: p for p in candidates}
    # Namespaced per board: a live search provider (e.g. SerpAPI) returns a
    # different, query-dependent candidate set on every call. A namespace
    # shared across boards/refinements accumulates every candidate set ever
    # seen, so `store.query(top_k=len(candidates))` can return ids from a
    # *different* board's leftovers that outrank this board's own freshly
    # upserted vectors — those get silently dropped by the `by_id` filter
    # below, potentially zeroing out results entirely. Scoping by board_id
    # keeps each board's ranking pool isolated. Re-upserting every call (not
    # gating on a count match) is still correct/necessary on top of this: it
    # keeps a re-run of the *same* board fresh after a refine changes its
    # candidate set. Embedding is self-hosted CLIP (no per-call cost).
    namespace = f"products:{provider.name}:{embedder.key}:{board_id}"
    texts = [_product_text(p) for p in candidates]
    vectors = embedder.embed_texts(texts)
    store.upsert(namespace, [p.id for p in candidates], vectors)
    logger.info("Indexed %d products into %s", len(candidates), namespace)

    hits = store.query(namespace, profile, top_k=len(candidates))

    # Blend vector similarity with palette affinity, keep top N. results_count
    # is intentionally larger than a single grid page so the frontend can
    # reveal more of the same ranked pool ("show more") without another call.
    scored: list[tuple[float, float, Product]] = []
    for pid, sim in hits:
        product = by_id.get(pid)
        if product is None:
            continue
        pal = _palette_affinity(product.color, vibe.palette)
        scored.append((0.75 * sim + 0.25 * pal, pal, product))
    scored.sort(key=lambda t: -t[0])
    top = scored[: settings.results_count]

    products = []
    for final_score, pal, product in top:
        entry = product.model_dump()
        entry["similarity"] = round(float(final_score), 4)
        entry["why_matched"] = _why_matched(product, vibe, pal)
        products.append(entry)

    return {
        "board_id": board_id,
        "vibe": vibe.to_dict(),
        "products": products,
    }


def analyze_board(board: Board) -> dict[str, Any]:
    if board.analysis is not None:
        # FR-2.4: re-runs of the same board cost nothing.
        return board.analysis

    settings = get_settings()
    embedder = get_embedding_provider()

    # 1. Per-image embeddings → board profile (normalized mean).
    image_vecs = embedder.embed_images(board.image_paths)
    profile = normalize(image_vecs.mean(axis=0, keepdims=True))[0]

    # 2. Representative sampling: images closest to the profile centroid go
    #    to the vision-LLM (cost control — never the whole board).
    sims_to_profile = image_vecs @ profile
    sample_idx = np.argsort(-sims_to_profile)[: settings.vibe_sample_size]
    sampled_paths = [board.image_paths[i] for i in sample_idx]

    # 3. "Your Vibe" summary. A live LLM failure must not kill the pipeline.
    summarizer = get_vibe_summarizer()
    if _is_gemini(summarizer) and not _gemini_budget.try_consume():
        logger.warning("Gemini daily budget exhausted — serving the stub vibe summary instead")
        vibe = StubVibeSummarizer().summarize(sampled_paths)
    else:
        try:
            vibe = summarizer.summarize(sampled_paths)
        except Exception as exc:
            logger.warning("Vibe summarizer failed (%s) — falling back to stub", exc)
            vibe = StubVibeSummarizer().summarize(sampled_paths)

    # 4. Candidate products, ranked against the board profile.
    result = _rank_and_package(board.id, profile, vibe)

    board.profile = profile
    board.vibe = vibe
    board.analysis = result
    return result


def refine_board(board: Board, feedback: str) -> dict[str, Any]:
    """Nudge an already-analyzed board's results with free-text feedback
    ("more colorful", "no black, prefer skirts") without re-touching the
    source images: text-only vibe refinement (cheap, no vision-LLM call
    needed) plus a lightweight embedding nudge on the board profile."""
    if board.profile is None or board.vibe is None:
        raise ValueError("Board has not been analyzed yet")

    embedder = get_embedding_provider()
    summarizer = get_vibe_summarizer()
    if _is_gemini(summarizer) and not _gemini_budget.try_consume():
        logger.warning("Gemini daily budget exhausted — serving the stub refine instead")
        vibe = StubVibeSummarizer().refine(board.vibe, feedback)
    else:
        try:
            vibe = summarizer.refine(board.vibe, feedback)
        except Exception as exc:
            logger.warning("Vibe refine failed (%s) — falling back to stub", exc)
            vibe = StubVibeSummarizer().refine(board.vibe, feedback)

    feedback_vec = embedder.embed_texts([feedback])[0]
    profile = normalize((0.7 * board.profile + 0.3 * feedback_vec)[None, :])[0]

    result = _rank_and_package(board.id, profile, vibe)

    board.profile = profile
    board.vibe = vibe
    board.analysis = result
    return result
