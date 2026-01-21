"""
Mock provider for testing Ministudio without API calls.
"""

import asyncio
from typing import Any
from .base import BaseVideoProvider
from ..interfaces import VideoGenerationRequest, VideoGenerationResult


class MockVideoProvider(BaseVideoProvider):
    """Mock provider for testing without API calls"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return "mock"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        await asyncio.sleep(1)  # Simulate processing time

        # Create a simple test video (in reality, would be actual video bytes)
        # For now, we'll just return success without actual video
        return VideoGenerationResult(
            success=True,
            provider=self.name,
            video_bytes=b"mock_video_bytes",
            generation_time=1.0,
            metadata={
                "mock": True,
                "prompt": request.prompt,
                "duration": request.duration_seconds
            }
        )
