"""
Google Vertex AI provider for Ministudio.
"""

import time
import asyncio
from typing import Any
from .base import BaseVideoProvider
from ..core import VideoGenerationRequest, VideoGenerationResult


class VertexAIProvider(BaseVideoProvider):
    """Google Vertex AI (Veo) provider"""

    def __init__(self, project_id: str, location: str = "us-central1", **kwargs):
        super().__init__(**kwargs)
        self.project_id = project_id
        self.location = location
        self._client = None

    @property
    def name(self) -> str:
        return "google-vertex-ai"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        start_time = time.time()

        try:
            # Lazy import
            from google.genai import types
            from google import genai

            if self._client is None:
                self._client = genai.Client(
                    project=self.project_id,
                    location=self.location,
                    vertexai=True
                )

            source = types.GenerateVideosSource(prompt=request.prompt)
            config = types.GenerateVideosConfig(
                aspect_ratio=request.aspect_ratio,
                duration_seconds=request.duration_seconds
            )

            operation = self._client.models.generate_videos(
                model="veo-3.1-generate-preview",
                source=source,
                config=config
            )

            # Poll for completion (simplified - in reality would be async)
            while not operation.done:
                await asyncio.sleep(5)
                operation = self._client.operations.get(operation)

            response = operation.result
            if response and response.generated_videos:
                video = response.generated_videos[0]
                video_bytes = video.video.video_bytes or video.video.bytes

                return VideoGenerationResult(
                    success=True,
                    video_bytes=video_bytes,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    metadata={
                        "model": "veo-3.1",
                        "operation_id": operation.name
                    }
                )

            return VideoGenerationResult(
                success=False,
                provider=self.name,
                generation_time=time.time() - start_time,
                error="No video generated"
            )

        except Exception as e:
            return VideoGenerationResult(
                success=False,
                provider=self.name,
                generation_time=time.time() - start_time,
                error=str(e)
            )

    def estimate_cost(self, duration_seconds: int) -> float:
        # Vertex AI pricing estimate (subject to change)
        return duration_seconds * 0.05  # Example: $0.05 per second
