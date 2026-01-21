"""
Google Vertex AI provider for Ministudio.
"""

import time
import asyncio
import json
import logging
import os
import re
from typing import Any, Optional, Dict
from google.oauth2 import service_account
from .base import BaseVideoProvider
from ..interfaces import VideoGenerationRequest, VideoGenerationResult

logger = logging.getLogger(__name__)


def load_gcp_credentials() -> tuple[Optional[service_account.Credentials], Optional[str]]:
    """
    Load GCP credentials from environment variables with high resilience to escaping issues.

    Supports multiple credential sources:
    - GCP_SERVICE_ACCOUNT_JSON: Full JSON string
    - GCP_SA_KEY: Alternative JSON string
    - GOOGLE_APPLICATION_CREDENTIALS: Path to JSON file or JSON content
    - Individual env vars: GCP_PROJECT_ID, GCP_CLIENT_EMAIL, GCP_PRIVATE_KEY

    Returns:
        Tuple of (credentials, project_id) or (None, None) if loading fails
    """
    sa_key = (
        os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        or os.getenv("GCP_SA_KEY")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )

    if not sa_key:
        logger.warning(
            "No GCP credential source found in environment variables")
        return None, None

    sa_info: Optional[Dict[str, Any]] = None

    # Strategy 1: Standard JSON parsing
    if not sa_info:
        try:
            sa_info = json.loads(sa_key)
            logger.info(
                "Successfully parsed GCP key using standard JSON parsing")
        except json.JSONDecodeError as e:
            logger.debug(f"Standard JSON parsing failed: {e}")

    # Strategy 2: ast.literal_eval fallback (for single-quoted dict strings)
    if not sa_info:
        try:
            import ast
            sa_info = ast.literal_eval(sa_key)
            if isinstance(sa_info, dict):
                logger.info(
                    "Successfully parsed GCP key using ast.literal_eval")
        except Exception as e:
            logger.debug(f"ast.literal_eval strategy failed: {e}")

    # Strategy 3: Handle escaped quotes or wrapped in quotes
    if not sa_info:
        try:
            fixed = sa_key.strip()

            # Remove outer quotes if present
            if (fixed.startswith('"') and fixed.endswith('"')) or \
               (fixed.startswith("'") and fixed.endswith("'")):
                fixed = fixed[1:-1]

            # Replace escaped quotes with regular quotes
            fixed = fixed.replace('\\"', '"').replace("\\'", "'")

            # Try JSON parsing again
            try:
                sa_info = json.loads(fixed)
                logger.info(
                    "Successfully parsed GCP key after unescaping quotes")
            except json.JSONDecodeError:
                # Try literal_eval on fixed string
                import ast
                sa_info = ast.literal_eval(fixed)
                if isinstance(sa_info, dict):
                    logger.info(
                        "Successfully parsed GCP key using literal_eval after unescaping")
        except Exception as e:
            logger.debug(f"Escape/quote fixing strategy failed: {e}")

    # Strategy 4: Regex extraction (Last Resort)
    if not sa_info:
        try:
            logger.debug("Attempting regex extraction from mangled JSON...")

            # Extract common fields
            project_id_match = re.search(
                r'["\']project_id["\']:\s*["\']([^"\']+)["\']', sa_key)
            private_key_match = re.search(
                r'["\']private_key["\']:\s*["\'](-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----\\n?)["\']', sa_key, re.DOTALL)
            client_email_match = re.search(
                r'["\']client_email["\']:\s*["\']([^"\']+)["\']', sa_key)

            if project_id_match and private_key_match and client_email_match:
                logger.info("Successfully extracted GCP fields using regex")
                private_key = private_key_match.group(1).replace("\\n", "\n")
                sa_info = {
                    "type": "service_account",
                    "project_id": project_id_match.group(1),
                    "private_key": private_key,
                    "client_email": client_email_match.group(1),
                    "private_key_id": "extracted-via-regex",
                    "client_id": "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "universe_domain": "googleapis.com",
                }
        except Exception as e:
            logger.debug(f"Regex extraction failed: {e}")

    # Strategy 5: Individual Secrets Fallback
    if not sa_info:
        project_id = os.getenv("GCP_PROJECT_ID")
        client_email = os.getenv("GCP_CLIENT_EMAIL")
        private_key = os.getenv("GCP_PRIVATE_KEY")

        if project_id and client_email and private_key:
            logger.info(
                "Constructing GCP credentials from individual environment variables")
            private_key = private_key.replace("\\n", "\n")
            if "BEGIN PRIVATE KEY" not in private_key:
                private_key = (
                    f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
                )

            sa_info = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID", "manual-id"),
                "private_key": private_key,
                "client_email": client_email,
                "client_id": os.getenv("GCP_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}",
                "universe_domain": "googleapis.com",
            }

    # Final check and credential creation
    if sa_info and isinstance(sa_info, dict):
        try:
            # Handle authorized user credentials differently if needed
            if sa_info.get("type") == "authorized_user":
                logger.warning(
                    "Authorized user credentials detected - may need different scope handling")

            credentials = service_account.Credentials.from_service_account_info(
                sa_info, scopes=[
                    "https://www.googleapis.com/auth/cloud-platform"]
            )
            project_id = sa_info.get(
                "project_id") or sa_info.get("quota_project_id")
            logger.info(
                f"Successfully loaded GCP credentials for project: {project_id}")
            return credentials, project_id

        except Exception as e:
            logger.error(
                f"Failed to create credentials from service account info: {e}")

    # Strategy 6: Application Default Credentials with explicit scopes
    try:
        import google.auth

        logger.info("Attempting to load Application Default Credentials...")

        # Check if GOOGLE_APPLICATION_CREDENTIALS is JSON content instead of a path
        adc_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if adc_path and adc_path.strip().startswith("{"):
            logger.info(
                "GOOGLE_APPLICATION_CREDENTIALS contains JSON content, writing to temp file...")
            temp_creds_path = "/tmp/google_creds.json"
            with open(temp_creds_path, "w") as f:
                f.write(adc_path)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path

        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        if credentials:
            logger.info(f"Successfully loaded ADC for project: {project_id}")
            return credentials, project_id
    except Exception as e:
        logger.debug(f"ADC fallback failed: {e}")

    logger.error("All GCP credential loading strategies failed")
    return None, None


class VertexAIProvider(BaseVideoProvider):
    """Google Vertex AI (Veo) provider with GCP authentication"""

    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1", **kwargs):
        super().__init__(**kwargs)
        self.location = location

        # Load GCP credentials
        self.credentials, loaded_project_id = load_gcp_credentials()

        if not self.credentials:
            raise ValueError(
                "Failed to load GCP credentials. Please set environment variables.")

        self.project_id = project_id or loaded_project_id
        if not self.project_id:
            raise ValueError(
                "Project ID not provided and could not be loaded from credentials.")

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
                    vertexai=True,
                    credentials=self.credentials
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
