"""
Ministudio - Model-Agnostic AI Video Generation
===============================================
Framework for generating consistent AI videos across multiple providers.
Plugin architecture for any AI model (OpenAI, Anthropic, Google, Local, etc.)

License: MIT
GitHub: https://github.com/aynaash/ministudio
"""

import os
import sys
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

from ministudio.config import VideoConfig, DEFAULT_CONFIG
from ministudio.interfaces import VideoGenerationRequest, VideoGenerationResult, VideoProvider
from ministudio.orchestrator import VideoOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class StyleConfig:
    """Legacy Configuration for visual style consistency (Kept for backward compat)"""
    name: str = "ghibli"
    description: str = "Studio Ghibli aesthetic"
    characters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    technical: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoTemplate:
    """Reusable template (Legacy/Placeholder)"""
    name: str
    description: str
    duration: int = 8

    def render_prompt(self, **kwargs):
        return ""


# ============================================
# MINISTUDIO CORE
# ============================================


class Ministudio:
    """Main orchestrator for model-agnostic video generation"""

    def __init__(self,
                 provider: VideoProvider,
                 output_dir: str = "./ministudio_output"):

        self.provider = provider
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the Orchestrator (The Kubernetes Controller)
        self.orchestrator = VideoOrchestrator(provider)

        # Register built-in providers
        self._available_providers = {}
        self._register_builtin_providers()

    def _register_builtin_providers(self):
        """Register all available provider implementations"""
        # Import here to avoid circular imports
        try:
            from .providers.mock import MockVideoProvider
            self._available_providers["mock"] = MockVideoProvider
        except ImportError:
            logger.warning("Mock provider not available")

        try:
            from .providers.vertex_ai import VertexAIProvider
            self._available_providers["vertex-ai"] = VertexAIProvider
        except ImportError:
            logger.warning("Vertex AI provider not available")

        try:
            from .providers.openai_sora import OpenAISoraProvider
            self._available_providers["openai-sora"] = OpenAISoraProvider
        except ImportError:
            logger.warning("OpenAI Sora provider not available")

        try:
            from .providers.local import LocalVideoProvider
            self._available_providers["local"] = LocalVideoProvider
        except ImportError:
            logger.warning("Local provider not available")

    @classmethod
    def create_provider(cls,
                        provider_type: str,
                        **provider_kwargs) -> VideoProvider:
        """Factory method to create a provider"""

        # Try to import dynamically
        try:
            if provider_type == "vertex-ai":
                from .providers.vertex_ai import VertexAIProvider
                from .providers.vertex_ai import load_gcp_credentials

                # Check for explicit creds or env vars
                if "project_id" not in provider_kwargs and "credentials" not in provider_kwargs:
                    creds, pid = load_gcp_credentials()
                    if pid:
                        provider_kwargs["project_id"] = pid

                return VertexAIProvider(**provider_kwargs)
            elif provider_type == "openai-sora":
                from .providers.openai_sora import OpenAISoraProvider
                return OpenAISoraProvider(**provider_kwargs)
            elif provider_type == "local":
                from .providers.local import LocalVideoProvider
                return LocalVideoProvider(**provider_kwargs)
            elif provider_type == "mock":
                from .providers.mock import MockVideoProvider
                return MockVideoProvider(**provider_kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider_type}")
        except ImportError as e:
            raise ValueError(f"Provider {provider_type} not available: {e}")

    async def generate_concept_video(self,
                                     concept: str,
                                     action: str,
                                     duration: int = 8,
                                     mood: str = "magical",
                                     filename: Optional[str] = None,
                                     config: Optional[VideoConfig] = None) -> VideoGenerationResult:
        """Generate a single video using the Orchestrator"""

        # Update config with inline parameters if provided
        if config:
            target_config = config
        else:
            target_config = VideoConfig(duration_seconds=duration, mood=mood)

        # Delegate to Orchestrator
        logger.info(f"Orchestrating generation for: {concept} - {action}")
        result = await self.orchestrator.schedule_generation(concept, action, target_config)

        # Save result logic
        if result.success and result.video_bytes:
            if filename is None:
                filename = f"{concept.replace(' ', '_')}_{int(time.time())}.mp4"

            output_path = self.output_dir / filename
            output_path.write_bytes(result.video_bytes)
            result.video_path = output_path
            logger.info(f"Video saved to: {output_path}")

        return result

    async def generate_segmented_video(self, segments: List[Dict[str, Any]], base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        Generate a segmented video with state persistence.
        Delegates to Orchestrator's sequence generation.
        """
        if base_config is None:
            base_config = DEFAULT_CONFIG

        return await self.orchestrator.generate_sequence(segments, base_config)
