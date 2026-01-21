"""
Core interfaces/protocols for Ministudio.
Moved here to avoid circular imports.
"""

from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VideoGenerationRequest:
    """Standardized request for video generation"""
    prompt: str
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    style_guidance: Optional[Dict[str, Any]] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "duration_seconds": self.duration_seconds,
            "aspect_ratio": self.aspect_ratio,
            "style_guidance": self.style_guidance or {},
            "negative_prompt": self.negative_prompt,
            "seed": self.seed
        }


@dataclass
class VideoGenerationResult:
    """Standardized result from video generation"""
    success: bool
    video_path: Optional[Path] = None
    video_bytes: Optional[bytes] = None
    provider: str = "unknown"
    generation_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_video(self) -> bool:
        return bool(self.video_path or self.video_bytes)


@runtime_checkable
class VideoProvider(Protocol):
    """Protocol for video generation providers"""

    @property
    def name(self) -> str:
        """Name of the provider"""
        ...

    @property
    def supported_aspect_ratios(self) -> List[str]:
        """List of supported aspect ratios"""
        ...

    @property
    def max_duration(self) -> int:
        """Maximum duration in seconds"""
        ...

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate a video from a request"""
        ...

    def estimate_cost(self, duration_seconds: int) -> float:
        """Estimate cost in USD for generation"""
        ...
