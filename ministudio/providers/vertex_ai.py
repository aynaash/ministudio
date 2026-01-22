"""
Enhanced Vertex AI provider with URI download support
"""
import os
import re
import json
import time
import io
import mimetypes
import asyncio
import logging
from typing import Optional, Dict, Any
from google.oauth2 import service_account

from .base import BaseVideoProvider
from ..interfaces import VideoGenerationRequest, VideoGenerationResult
from ..utils import load_gcp_credentials

logger = logging.getLogger(__name__)


class VertexAIProvider(BaseVideoProvider):
    """Google Vertex AI (Veo) provider with GCP authentication and URI download support"""

    def __init__(self,
                 project_id: Optional[str] = None,
                 location: str = "us-central1",
                 api_key: Optional[str] = None,
                 credentials: Optional[service_account.Credentials] = None):

        self.project_id = project_id
        self.location = location
        self.credentials = credentials
        self.api_key = api_key
        self._client = None

        # 1. Prioritize Cloud Authentication (Vertex AI)
        if not self.credentials:
            try:
                # Attempt to load Application Default Credentials or from env
                creds, pid = load_gcp_credentials()
                if creds:
                    self.credentials = creds
                    if not self.project_id:
                        self.project_id = pid
                        logger.debug(
                            f"Detected GCP Project ID: {self.project_id}")
            except Exception as e:
                logger.debug(f"Vertex AI auth check skipped/failed: {e}")

        # 2. If no Cloud credentials, fallback to API Key (AI Studio)
        if not self.project_id and not self.credentials:
            if not self.api_key:
                self.api_key = os.getenv(
                    "VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")

            if self.api_key:
                logger.info(
                    "Initializing in AI Studio mode (API Key detected)")
            else:
                raise ValueError(
                    "Authentication failed: Could not find GCP Project ID or an API Key. "
                    "Please set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_API_KEY."
                )
        else:
            logger.info(
                f"Initializing in Vertex AI mode (Project: {self.project_id})")

    @property
    def name(self) -> str:
        return "google-vertex-ai"

    @property
    def max_duration(self) -> int:
        return 8  # Veo model limit

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        start_time = time.time()

        try:
            # Lazy import
            from google.genai import types
            from google import genai

            if self._client is None:
                # Initialize client based on auth method
                # API Key and Project/Location are mutually exclusive in the google-genai SDK
                if self.api_key:
                    logger.debug("Initializing Client with API Key")
                    self._client = genai.Client(
                        api_key=self.api_key,
                        vertexai=False  # API keys are for AI Studio/Gemini API
                    )
                else:
                    logger.debug(
                        f"Initializing Client with Vertex AI (Project: {self.project_id})")
                    self._client = genai.Client(
                        project=self.project_id,
                        location=self.location,
                        vertexai=True,
                        credentials=self.credentials
                    )

            # Model constraints: veo-3.1-generate-preview supports 4-8 seconds
            duration = request.duration_seconds
            if duration < 4:
                logger.warning(
                    f"Requested duration {duration}s is too short. Clamping to 4s.")
                duration = 4
            elif duration > 8:
                logger.warning(
                    f"Requested duration {duration}s is too long for preview model. Clamping to 8s.")
                duration = 8

            # Prepare Grounding Anchors
            image_anchor = None

            # 1. Primary Image (First Frame Grounding)
            if request.starting_frames:
                try:
                    anchor_path = request.starting_frames[0]
                    if os.path.exists(anchor_path):
                        mime_type, _ = mimetypes.guess_type(anchor_path)
                        with open(anchor_path, 'rb') as f:
                            image_anchor = types.Image(
                                image_bytes=f.read(),
                                mime_type=mime_type or 'image/png'
                            )
                        logger.info(
                            f"Using first frame anchor: {anchor_path} (MIME: {mime_type})")
                except Exception as e:
                    logger.warning(f"Failed to load first frame anchor: {e}")

            # 2. Reference Images (Style/Character Grounding)
            # Veo 3.1 supports up to 3 reference images
            reference_images = []
            anchors_to_check = []

            # Prioritize character samples
            if request.character_samples:
                for char_name, samples in request.character_samples.items():
                    anchors_to_check.extend(samples)

            # Then background samples
            if request.background_samples:
                anchors_to_check.extend(request.background_samples)

            # Take the first 3 unique valid paths
            unique_anchors = list(dict.fromkeys(anchors_to_check))
            for anchor_path in unique_anchors[:3]:
                if os.path.exists(anchor_path):
                    try:
                        mime_type, _ = mimetypes.guess_type(anchor_path)
                        with open(anchor_path, 'rb') as f:
                            ref_image = types.Image(
                                image_bytes=f.read(),
                                mime_type=mime_type or 'image/png'
                            )
                            reference_images.append(
                                types.VideoGenerationReferenceImage(
                                    image=ref_image,
                                    reference_type="asset"
                                )
                            )
                        logger.info(
                            f"Adding reference image: {anchor_path} (MIME: {mime_type})")
                    except Exception as e:
                        logger.warning(
                            f"Failed to load reference image {anchor_path}: {e}")

            # 3. Video-to-Video (Continuity)
            # Note: Veo 3.1 extension only supports videos from previous generations
            # but we'll try to pass bytes if it's a local path, though it might fail.
            if request.starting_frames and len(request.starting_frames) > 0:
                # If it's a video file, it's captured in starting_frames
                # But Veo 3.1 primary 'image' handles the first frame.
                # 'video' is primarily for extension.
                pass

            # Model constraints: duration must be 8s for reference images, 1080p, or 4k
            if reference_images or request.aspect_ratio == "9:16":
                if duration != 8:
                    logger.info(
                        f"Setting duration to 8s as required for reference images/portrait mode.")
                    duration = 8

            config = types.GenerateVideosConfig(
                aspect_ratio=request.aspect_ratio,
                duration_seconds=duration,
                reference_images=reference_images if reference_images else None
            )

            # Use preview model (matches working script)
            # Flattened call: pass prompt, image, video as direct kwargs
            operation = self._client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=request.prompt,
                image=image_anchor,
                video=None,  # Video parameter is restricted to Veo-generated videos
                config=config
            )

            # Poll for completion (using synchronous sleep as per Google docs)
            poll_count = 0
            max_polls = 120  # 10 minutes max
            while not operation.done:
                logger.info(
                    "Video has not been generated yet. Checking again in 10 seconds...")
                time.sleep(10)
                operation = self._client.operations.get(operation)
                poll_count += 1
                if poll_count >= max_polls:
                    logger.error("Video generation timed out after 10 minutes")
                    return VideoGenerationResult(
                        success=False,
                        provider=self.name,
                        generation_time=time.time() - start_time,
                        error="Generation timed out"
                    )

            logger.info(f"Video generation completed after {poll_count * 10}s")

            # Check for API errors first
            if hasattr(operation, 'error') and operation.error:
                error_msg = operation.error.get('message', str(operation.error)) if isinstance(
                    operation.error, dict) else str(operation.error)
                logger.error(f"API error: {error_msg}")
                return VideoGenerationResult(
                    success=False,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    error=error_msg
                )

            # Get response following Google docs pattern
            response = operation.result
            if not response:
                logger.error(
                    "Error occurred while generating video - no response")
                return VideoGenerationResult(
                    success=False,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    error="No response from video generation"
                )

            generated_videos = response.generated_videos
            if not generated_videos:
                logger.error("No videos were generated")
                return VideoGenerationResult(
                    success=False,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    error="No videos in response"
                )

            logger.info(f"Generated {len(generated_videos)} video(s)")

            # Get the first video
            generated_video = generated_videos[0]
            if not generated_video.video:
                logger.error("Video object is empty")
                return VideoGenerationResult(
                    success=False,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    error="Video object is empty"
                )

            # Extract video bytes - try different attributes
            video_bytes = None
            video_obj = generated_video.video

            if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                video_bytes = video_obj.video_bytes
            elif hasattr(video_obj, 'bytes') and video_obj.bytes:
                video_bytes = video_obj.bytes
            elif hasattr(video_obj, 'uri'):
                # If it's a URI, we need to download it
                logger.info(f"Video stored at URI: {video_obj.uri}")
                try:
                    import requests
                    from google.auth.transport.requests import Request as AuthRequest

                    if not self.credentials.valid:
                        auth_req = AuthRequest()
                        self.credentials.refresh(auth_req)

                    headers = {
                        "Authorization": f"Bearer {self.credentials.token}"}
                    resp = requests.get(
                        video_obj.uri, headers=headers, timeout=300)
                    resp.raise_for_status()
                    video_bytes = resp.content
                    logger.info(
                        f"Downloaded video from URI: {len(video_bytes)} bytes")
                except Exception as e:
                    logger.error(f"Failed to download video from URI: {e}")
                    return VideoGenerationResult(
                        success=False,
                        provider=self.name,
                        generation_time=time.time() - start_time,
                        error=f"Failed to download video: {e}"
                    )

            if not video_bytes:
                logger.error("Could not extract video bytes from video object")
                logger.debug(f"Video object attributes: {dir(video_obj)}")
                return VideoGenerationResult(
                    success=False,
                    provider=self.name,
                    generation_time=time.time() - start_time,
                    error="Could not extract video bytes"
                )

            logger.info(
                f"Successfully extracted video: {len(video_bytes)} bytes")
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

        except Exception as e:
            logger.error(f"Video generation error: {e}", exc_info=True)
            return VideoGenerationResult(
                success=False,
                provider=self.name,
                generation_time=time.time() - start_time,
                error=str(e)
            )

    def estimate_cost(self, duration_seconds: int) -> float:
        # Vertex AI pricing estimate (subject to change)
        return duration_seconds * 0.05  # Example: $0.05 per second
