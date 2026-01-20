"""
Base provider classes for Ministudio video generation providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from ..core import VideoGenerationRequest, VideoGenerationResult


class BaseVideoProvider(ABC):
    """Base class for all video providers"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def supported_aspect_ratios(self) -> List[str]:
        return ["16:9", "1:1", "9:16"]

    @property
    def max_duration(self) -> int:
        return 60

    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        pass

    def estimate_cost(self, duration_seconds: int) -> float:
        return 0.0  # Default: free/unknown
