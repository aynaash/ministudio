"""
State Machine for Ministudio.
Manages the "World State" across sequential generations, ensuring consistency.
Acts like the etcd/state store in Kubernetes.
"""

import copy
import logging
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
    story_progress: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "environment": self.environment.to_dict() if self.environment else None,
            "style": self.style.to_dict() if self.style else None,
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
        # Simple extraction for now
        return {
            "previous_scene_id": recent[-1].scene_id,
            "character_states": {
                name: char.emotional_palette.get("current_emotion", "neutral")
                for name, char in recent[-1].characters.items()
            }
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

        if initial_config:
            self.update_from_config(initial_config)

    def update_from_config(self, config: VideoConfig):
        """Update state based on a new configuration (e.g. for the next scene)"""
        if config.characters:
            # Merge/Update characters
            for name, char in config.characters.items():
                self.characters[name] = char

        if config.environment:
            self.environment = config.environment

        if config.style_dna:
            self.style = config.style_dna

    def next_scene(self) -> WorldState:
        """Advance to the next scene, committing the current state"""
        self.current_scene_id += 1

        snapshot = WorldState(
            scene_id=self.current_scene_id,
            characters=copy.deepcopy(self.characters),
            environment=copy.deepcopy(self.environment),
            style=copy.deepcopy(self.style)
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
            style_dna=self.style
            # Note: other fields like lighting/camera are per-shot and might not persist
            # unless we add them to WorldState. For now, we assume they are per-shot.
        )
