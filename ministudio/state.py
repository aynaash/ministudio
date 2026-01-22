"""
State Machine for Ministudio.
Manages the "World State" across sequential generations, ensuring consistency.
Acts like the etcd/state store in Kubernetes.
"""

import copy
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .config import VideoConfig, Character, Environment, StyleDNA

logger = logging.getLogger(__name__)


@dataclass
class WorldState:
    """Snapshot of the world at a specific point in time (scene)"""
    scene_id: int
    characters: Dict[str, Character]
    environment: Optional[Environment]
    style: Optional[StyleDNA]
    output_video_path: Optional[Path] = None
    last_frames: List[str] = field(
        default_factory=list)  # Paths to extracted frames
    active_speaker: Optional[str] = None
    # Text of the previous narration/dialogue
    last_narration: Optional[str] = None
    conflict_matrix: Dict[str, str] = field(default_factory=dict)
    story_progress: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "environment": self.environment.to_dict() if self.environment else None,
            "style": self.style.to_dict() if self.style else None,
            "output_video_path": str(self.output_video_path) if self.output_video_path else None,
            "last_frames": self.last_frames,
            "active_speaker": self.active_speaker,
            "conflict_matrix": self.conflict_matrix,
            "story_progress": self.story_progress
        }


class StatePersistenceEngine:
    """
    Handles history and continuity.
    future: This would interface with a DB or vector store for long-term memory.
    """

    def __init__(self):
        self.history: List[WorldState] = []

    def save_snapshot(self, state: WorldState):
        """Commit a state snapshot to history"""
        # Deep copy to ensure immutability of history
        self.history.append(copy.deepcopy(state))

    def get_last_snapshot(self) -> Optional[WorldState]:
        if not self.history:
            return None
        return self.history[-1]

    def get_continuity_context(self, lookback: int = 1) -> Dict[str, Any]:
        """
        Get context from previous N scenes to help generated consistency.
        Returns a dict summarizing what just happened.
        """
        if not self.history:
            return {}

        recent = self.history[-lookback:]
        last = recent[-1]

        return {
            "previous_scene_id": last.scene_id,
            "character_states": {
                name: char.emotional_palette.get("current_emotion", "neutral")
                for name, char in last.characters.items()
            },
            "continuity_frames": last.last_frames
        }


class VideoStateMachine:
    """
    The "Kubernetes Controller" for State.
    Manages the transitions and updates of the world state.
    """

    def __init__(self, initial_config: Optional[VideoConfig] = None):
        self.persistence = StatePersistenceEngine()

        # Initialize active state
        self.current_scene_id = 0
        self.characters: Dict[str, Character] = {}
        self.environment: Optional[Environment] = None
        self.style: Optional[StyleDNA] = None
        self.conflict_matrix: Dict[str, str] = {}

        if initial_config:
            self.update_from_config(initial_config)

    def update_from_config(self, config: VideoConfig):
        """Update state based on a new configuration (e.g. for the next scene)"""
        if config.characters:
            # Merge/Update characters
            for name, char in config.characters.items():
                if name in self.characters:
                    # Update existing character: Preserve existing identity if not provided,
                    # but allow updates to current_state
                    existing = self.characters[name]
                    if hasattr(char, 'identity') and any(char.identity.values()):
                        existing.identity.update(char.identity)
                    if hasattr(char, 'current_state') and any(char.current_state.values()):
                        existing.current_state.update(char.current_state)
                    # Sync other fields
                    existing.voice_id = char.voice_id or existing.voice_id
                    existing.voice_profile = char.voice_profile or existing.voice_profile
                else:
                    self.characters[name] = char

        if config.environment:
            if self.environment and config.environment.location == self.environment.location:
                # Update existing environment context
                if hasattr(config.environment, 'identity') and any(config.environment.identity.values()):
                    self.environment.identity.update(
                        config.environment.identity)
                if hasattr(config.environment, 'current_context') and any(config.environment.current_context.values()):
                    self.environment.current_context.update(
                        config.environment.current_context)
            else:
                self.environment = config.environment

        if config.style_dna:
            self.style = config.style_dna

        # Conflict matrix update
        if hasattr(config, 'conflict_matrix') and config.conflict_matrix:
            self.conflict_matrix.update(config.conflict_matrix)

    def next_scene(self, video_path: Optional[Path] = None, frames: List[str] = None, speaker: Optional[str] = None, narration: Optional[str] = None) -> WorldState:
        """Advance to the next scene, committing the current state"""
        self.current_scene_id += 1

        snapshot = WorldState(
            scene_id=self.current_scene_id,
            characters=copy.deepcopy(self.characters),
            environment=copy.deepcopy(self.environment),
            style=copy.deepcopy(self.style),
            output_video_path=video_path,
            last_frames=frames or [],
            active_speaker=speaker,
            last_narration=narration,
            conflict_matrix=copy.deepcopy(self.conflict_matrix)
        )

        self.persistence.save_snapshot(snapshot)
        logger.info(f"State machine advanced to scene {self.current_scene_id}")
        return snapshot

    def get_current_state_as_config(self) -> VideoConfig:
        """Export current state back to a VideoConfig object"""
        # This is useful for re-hydrating the prompt engine
        return VideoConfig(
            characters=self.characters,
            environment=self.environment,
            style_dna=self.style,
            custom_metadata={
                "last_narration": self.persistence.get_last_snapshot().last_narration if self.persistence.get_last_snapshot() else None
            }
        )
