"""
Video Orchestrator.
The "Kubernetes Controller" that coordinates State, Compilation, and Execution.
"""

import logging
from typing import List, Dict, Any, Optional

from .config import VideoConfig, DEFAULT_CONFIG
from .state import VideoStateMachine
from .compiler import ProgrammaticPromptCompiler
from .interfaces import VideoProvider, VideoGenerationResult, VideoGenerationRequest

logger = logging.getLogger(__name__)


class VideoOrchestrator:
    def __init__(self, provider: VideoProvider):
        self.provider = provider
        # Each orchestrator manages a specific state machine (like a specific deployment)
        self.state_machine = VideoStateMachine()
        self.compiler = ProgrammaticPromptCompiler()

    async def schedule_generation(self,
                                  concept: str,
                                  action: str,
                                  config: Optional[VideoConfig] = None) -> VideoGenerationResult:
        """
        Execute a single video generation job.
        1. Update State
        2. Compile Prompt
        3. Execute Provider
        """
        if config is None:
            config = DEFAULT_CONFIG

        # 0. Ensure config has the action
        config.action_description = action

        # 1. Update State Machine with new config intent
        self.state_machine.update_from_config(config)

        # 2. Advance State (Commit)
        world_state = self.state_machine.next_scene()

        # 3. Compile Prompt using the FULL config (merged with state)
        # We need to construct a "Resolution" config that combines:
        # - The transient config (action, specific lighting)
        # - The persistent state (characters, environment)

        # Start with the persistent state as a base config
        resolution_config = self.state_machine.get_current_state_as_config()

        # Merge in the specific request's config (which overrides persistent state if specified)
        # Note: In a real logic we might be recursive, but simple merge for now
        # We manually copy over the non-state things from the request config
        resolution_config.action_description = action
        if config.cinematography:
            resolution_config.cinematography = config.cinematography
        if config.lighting:
            resolution_config.lighting = config.lighting
        if config.continuity:
            resolution_config.continuity = config.continuity
        resolution_config.duration_seconds = config.duration_seconds

        # Compile
        compiled_prompt = self.compiler.compile(resolution_config)
        # Fallback if compile returns empty (e.g. no fancy config)
        final_prompt = compiled_prompt if compiled_prompt.strip(
        ) else f"{concept}: {action}"

        logger.info(f"Compiled Prompt Length: {len(final_prompt)}")
        logger.debug(f"Compiled Prompt: {final_prompt}")

        # 4. execute
        request = VideoGenerationRequest(
            prompt=final_prompt,
            duration_seconds=config.duration_seconds,
            aspect_ratio=config.aspect_ratio,
            negative_prompt=config.negative_prompt,
            seed=config.seed
        )

        result = await self.provider.generate_video(request)

        # 5. Future: Capture result into state (feedback loop)

        return result

    async def generate_sequence(self,
                                segments: List[Dict[str, Any]],
                                base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        Orchestrate a sequence of scenes.
        """
        if base_config:
            self.state_machine.update_from_config(base_config)

        results = []
        for segment in segments:
            # Create a transient config choice for this segment
            # This is where we would interpret "storyboard-as-code"
            seg_config = base_config or VideoConfig()  # fallback

            # Simple override if segment has specific state updates (legacy support)
            # In the new system, we'd look for specific `Character` objects in the segment dict

            concept = segment.get("concept", "")
            action = segment.get("action", "")

            result = await self.schedule_generation(concept, action, seg_config)
            results.append(result)

        return results
