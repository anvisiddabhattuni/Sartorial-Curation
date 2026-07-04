from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VibeResult:
    tags: list[str]
    palette: list[str]  # hex colors, dominant first
    sentence: str
    query_terms: list[str] = field(default_factory=list)  # product search queries
    stubbed: bool = False

    def to_dict(self) -> dict:
        return {
            "tags": self.tags,
            "palette": self.palette,
            "sentence": self.sentence,
            "stubbed": self.stubbed,
        }


class VibeSummarizer(ABC):
    """Turns a sampled subset of board images into the human-readable
    "Your Vibe" summary (tags, palette, one sentence) plus product query terms.

    Implementations: GeminiVibeSummarizer (vision-LLM, low-detail images for
    cost control) and StubVibeSummarizer (pure color analysis)."""

    @abstractmethod
    def summarize(self, image_paths: list[Path]) -> VibeResult: ...

    @abstractmethod
    def refine(self, previous: VibeResult, feedback: str) -> VibeResult:
        """Fold free-text user feedback ("more colorful", "no black") into an
        already-computed vibe. Text-only — no images re-sent, since the board's
        actual palette/photos haven't changed, only how we search/describe."""
