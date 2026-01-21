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
from typing import Dict, List, Optional, Any, Protocol, runtime_checkable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

from ministudio.config import VideoConfig, DEFAULT_CONFIG, SceneConfig, ShotConfig, Character, Environment
from ministudio.interfaces import VideoGenerationRequest, VideoGenerationResult, VideoProvider
from ministudio.orchestrator import VideoOrchestrator
from ministudio.utils import merge_videos


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
        Saves each segment and automatically merges them into a master video.
        """
        if base_config is None:
            base_config = DEFAULT_CONFIG

        # Generate segments via orchestrator
        results = await self.orchestrator.generate_sequence(segments, base_config)

        # Save each segment to the output directory
        for i, (segment, result) in enumerate(zip(segments, results)):
            if result.success and result.video_bytes:
                concept = segment.get("concept", f"segment_{i}")
                filename = f"seg_{i:02d}_{concept.replace(' ', '_')}_{int(time.time())}.mp4"

                output_path = self.output_dir / filename
                output_path.write_bytes(result.video_bytes)
                result.video_path = output_path
                logger.info(f"Segment {i} saved to: {output_path}")

        # Automatic Merge logic
        if results and all(r.success and r.video_path for r in results):

            merged_filename = f"master_story_{int(time.time())}.mp4"
            merged_path = self.output_dir / merged_filename

            video_paths = [r.video_path for r in results]
            success = merge_videos(video_paths, merged_path)

            if success:
                logger.info(
                    f"Master Story merged successfully: {merged_path}")
            else:
                logger.error("Failed to merge segments into Master Story.")

        return results

    async def generate_scene(self, scene: Union[Dict[str, Any], SceneConfig], base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        Generate a single cinematic scene.
        """
        if isinstance(scene, dict):
            # Hydrate from dict if needed
            scene_obj = SceneConfig()
            scene_obj.concept = scene.get("concept", "")
            scene_obj.mood = scene.get("mood", "magical")
            scene_obj.conflict_matrix = scene.get("conflict_matrix", {})

            if "characters" in scene:
                for name, data in scene["characters"].items():
                    char_data = data.copy()
                    if "voice_profile" in char_data and isinstance(char_data["voice_profile"], dict):
                        from ministudio.config import VoiceProfile
                        char_data["voice_profile"] = VoiceProfile(
                            **char_data["voice_profile"])
                    scene_obj.characters[name] = Character(
                        name=name, **char_data)

            if "environment" in scene:
                scene_obj.environment = Environment(**scene["environment"])

            if "shots" in scene:
                for shot_data in scene["shots"]:
                    # Hydrate shot-level overrides if present
                    try:
                        shot_obj = ShotConfig(
                            **{k: v for k, v in shot_data.items() if k not in ["characters", "environment"]})
                    except TypeError as e:
                        logger.error(
                            f"ShotConfig hydration failed: {e}. Data: {shot_data}")
                        raise
                    if "characters" in shot_data:
                        shot_obj.characters = {name: Character(
                            name=name, **c) for name, c in shot_data["characters"].items()}
                    if "environment" in shot_data:
                        shot_obj.environment = Environment(
                            **shot_data["environment"])
                    scene_obj.shots.append(shot_obj)

            scene = scene_obj

        results = await self.orchestrator.generate_scene(scene, base_config)

        # Save results
        for i, result in enumerate(results):
            if result.success and result.video_bytes:
                filename = f"scene_{scene.concept.replace(' ', '_')}_shot_{i}_{int(time.time())}.mp4"
                output_path = self.output_dir / filename
                output_path.write_bytes(result.video_bytes)
                result.video_path = output_path

        return results

    async def generate_film(self, film_spec: Union[str, Path, Dict[str, Any]], base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        The High-Level "Filmaking API".
        Generates a full story from a JSON/YAML spec.
        """
        if isinstance(film_spec, (str, Path)):
            path = Path(film_spec)
            if path.suffix == ".json":
                with open(path, "r") as f:
                    film_spec = json.load(f)
            elif path.suffix in [".yaml", ".yml"]:
                import yaml
                with open(path, "r") as f:
                    film_spec = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")

        all_results = []
        scenes_data = film_spec.get("scenes", [])

        logger.info(f"Generating film: {film_spec.get('title', 'Untitled')}")
        logger.info(f"Total scenes: {len(scenes_data)}")

        for i, scene_data in enumerate(scenes_data):
            logger.info(f"Processing Scene {i+1}/{len(scenes_data)}")
            scene_results = await self.generate_scene(scene_data, base_config)
            all_results.extend(scene_results)

        # Final merge
        if all_results and all(r.success and r.video_path for r in all_results):
            merged_filename = f"film_{film_spec.get('title', 'story').replace(' ', '_')}_{int(time.time())}.mp4"
            merged_path = self.output_dir / merged_filename

            from ministudio.utils import merge_videos_with_audio
            success = merge_videos_with_audio(all_results, merged_path)

            if success:
                logger.info(
                    f"Film produced successfully! Location: {merged_path}")

        return all_results
