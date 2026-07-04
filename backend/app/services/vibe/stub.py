"""Stub vibe summarizer: real color analysis, canned-but-sensible tags.
Used when no Gemini key is configured or the API call fails."""

import colorsys
import re
from pathlib import Path

from .base import VibeResult, VibeSummarizer
from .palette import extract_palette

_NEGATORS = {"no", "not", "without", "less", "avoid", "skip", "never"}
_AFFIRMERS = {"more", "prefer", "add", "want", "with", "some", "like"}
_SPLIT_RE = re.compile(r",|\band\b|\bbut\b", re.IGNORECASE)


def _describe_palette(palette: list[str]) -> tuple[list[str], list[str]]:
    hues = []
    lights = []
    sats = []
    for hex_color in palette:
        r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        hues.append(h)
        lights.append(l)
        sats.append(s)

    avg_light = sum(lights) / len(lights)
    avg_sat = sum(sats) / len(sats)

    tags: list[str] = []
    terms: list[str] = []
    if avg_sat < 0.22:
        tags.append("neutral palette")
        terms.extend(["beige linen trousers", "cream knit sweater"])
    elif avg_sat > 0.5:
        tags.append("bold color")
        terms.extend(["statement colorful top", "vibrant midi skirt"])
    else:
        tags.append("soft tones")
        terms.extend(["muted pastel cardigan", "washed cotton shirt"])

    if avg_light > 0.65:
        tags.extend(["airy", "clean lines"])
        terms.append("white oversized shirt")
    elif avg_light < 0.35:
        tags.extend(["moody", "layered"])
        terms.append("black wool overcoat")
    else:
        tags.extend(["easygoing", "everyday staples"])
        terms.append("relaxed straight-leg jeans")

    tags.append("effortless")
    return tags[:6], terms


def _parse_feedback(feedback: str) -> tuple[list[str], list[str]]:
    """Very lightweight include/exclude parsing for offline refinement, e.g.
    "no black, more skirts" -> excludes=["black"], includes=["skirts"]."""
    includes: list[str] = []
    excludes: list[str] = []
    for clause in _SPLIT_RE.split(feedback.lower()):
        words = [w for w in re.split(r"\s+", clause.strip()) if w]
        if not words:
            continue
        if words[0] in _NEGATORS:
            phrase = " ".join(words[1:]).strip()
            if phrase:
                excludes.append(phrase)
        else:
            phrase = " ".join(w for w in words if w not in _AFFIRMERS).strip()
            if phrase:
                includes.append(phrase)
    return includes, excludes


class StubVibeSummarizer(VibeSummarizer):
    def summarize(self, image_paths: list[Path]) -> VibeResult:
        palette = extract_palette(image_paths)
        tags, terms = _describe_palette(palette)
        sentence = (
            "A considered mix of "
            + tags[0]
            + " pieces with an "
            + tags[-1]
            + ", wearable feel."
        )
        return VibeResult(
            tags=tags,
            palette=palette,
            sentence=sentence,
            query_terms=terms,
            stubbed=True,
        )

    def refine(self, previous: VibeResult, feedback: str) -> VibeResult:
        includes, excludes = _parse_feedback(feedback)

        def _keep(phrase: str) -> bool:
            low = phrase.lower()
            return not any(x in low for x in excludes)

        tags = [t for t in previous.tags if _keep(t)] + [p for p in includes if p not in previous.tags]
        terms = [t for t in previous.query_terms if _keep(t)] + [p for p in includes if p not in previous.query_terms]

        sentence = previous.sentence
        if includes:
            sentence += " Now leaning into " + ", ".join(includes) + "."
        if excludes:
            sentence += " Steering clear of " + ", ".join(excludes) + "."

        return VibeResult(
            tags=tags[:6] or previous.tags,
            palette=previous.palette,
            sentence=sentence,
            query_terms=terms[:6] or previous.query_terms,
            stubbed=True,
        )
