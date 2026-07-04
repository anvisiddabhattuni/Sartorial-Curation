"""Stub vibe summarizer: real color analysis, canned-but-sensible tags.
Used when no Gemini key is configured or the API call fails."""

import colorsys
from pathlib import Path

from .base import VibeResult, VibeSummarizer
from .palette import extract_palette


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
