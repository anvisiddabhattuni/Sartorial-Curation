import json
import logging
from io import BytesIO
from pathlib import Path

from PIL import Image

from .base import VibeResult, VibeSummarizer
from .palette import extract_palette

logger = logging.getLogger("muse.vibe")

PROMPT = """You are a fashion stylist analyzing a mood board. These images together
express ONE aesthetic. Analyze the board as a whole, not image by image.

Return ONLY a JSON object with exactly these keys:
- "tags": 4-6 short lowercase aesthetic tags (e.g. "coastal", "relaxed tailoring", "neutral palette")
- "palette": 4-6 dominant hex colors of the overall board, most dominant first
- "sentence": one warm, specific sentence (max 25 words) describing the board's style
- "query_terms": 4-6 concrete product search queries matching the vibe
  (e.g. "linen wide-leg trousers", "oversized cream knit sweater")
"""

LOW_DETAIL_PX = 512  # cost control: downscale before sending to the vision-LLM

REFINE_PROMPT = """You are a fashion stylist refining a mood board summary based on
a user's follow-up feedback. You already described the board as:
- tags: {tags}
- sentence: "{sentence}"
- search terms: {query_terms}

The user now says: "{feedback}"

Update the summary to honor that feedback (add what they asked for, drop anything
they said no to) while keeping the parts of the original vibe they didn't object to.

Return ONLY a JSON object with exactly these keys:
- "tags": 4-6 short lowercase aesthetic tags
- "sentence": one warm, specific sentence (max 25 words) describing the updated style
- "query_terms": 4-6 concrete product search queries matching the updated vibe
"""


class GeminiVibeSummarizer(VibeSummarizer):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        from google import genai
        from google.genai import types

        # The SDK has no default timeout — an occasional stall on Gemini's
        # end would otherwise hang analyze_board forever, since a hang isn't
        # an exception the pipeline's stub-fallback try/except can catch.
        self._client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(timeout=20_000)
        )
        self._model = model

    def summarize(self, image_paths: list[Path]) -> VibeResult:
        from google.genai import types

        parts: list = [PROMPT]
        for p in image_paths:
            img = Image.open(p).convert("RGB")
            img.thumbnail((LOW_DETAIL_PX, LOW_DETAIL_PX))
            buf = BytesIO()
            img.save(buf, "JPEG", quality=80)
            parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"))

        response = self._client.models.generate_content(
            model=self._model,
            contents=parts,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
        data = json.loads(response.text)

        tags = [str(t) for t in data.get("tags", [])][:6]
        palette = [str(c) for c in data.get("palette", [])][:6]
        sentence = str(data.get("sentence", "")).strip()
        query_terms = [str(q) for q in data.get("query_terms", [])][:6]
        if not tags or not sentence:
            raise ValueError(f"Gemini returned incomplete vibe JSON: {data}")
        if not palette:
            palette = extract_palette(image_paths)
        return VibeResult(tags=tags, palette=palette, sentence=sentence, query_terms=query_terms)

    def refine(self, previous: VibeResult, feedback: str) -> VibeResult:
        from google.genai import types

        prompt = REFINE_PROMPT.format(
            tags=", ".join(previous.tags),
            sentence=previous.sentence,
            query_terms=", ".join(previous.query_terms),
            feedback=feedback,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
        data = json.loads(response.text)

        tags = [str(t) for t in data.get("tags", [])][:6]
        sentence = str(data.get("sentence", "")).strip()
        query_terms = [str(q) for q in data.get("query_terms", [])][:6]
        if not tags or not sentence or not query_terms:
            raise ValueError(f"Gemini returned incomplete refine JSON: {data}")
        # Palette reflects the board's actual photos, which haven't changed —
        # keep it rather than let a text-only call invent new colors.
        return VibeResult(tags=tags, palette=previous.palette, sentence=sentence, query_terms=query_terms)
