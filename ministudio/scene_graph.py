"""
Enhanced Scene Graph & World State
==================================
Advanced state management for cinematic continuity.

Features:
- Full scene graph with spatial relationships
- Character emotional arcs and positions
- Camera trajectory tracking
- Object persistence and physics
- Lighting evolution
- Conflict matrix for dramatic tension

Example:
    from ministudio.scene_graph import SceneGraph, Entity, CameraState
    
    graph = SceneGraph()
    graph.add_entity("emma", EntityType.CHARACTER, position=(0, 0, 0))
    graph.set_camera(CameraState(position=(0, 0, -5), target="emma"))
    graph.advance_frame()
"""

import json
import copy
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities in the scene."""
    CHARACTER = "character"
    PROP = "prop"
    ENVIRONMENT = "environment"
    LIGHT = "light"
    CAMERA = "camera"
    EFFECT = "effect"


class EmotionalState(Enum):
    """Character emotional states."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    CONTEMPT = "contempt"
    CURIOUS = "curious"
    DETERMINED = "determined"
    CONFUSED = "confused"
    HOPEFUL = "hopeful"
    ANXIOUS = "anxious"


@dataclass
class Vector3:
    """3D position/direction vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> "Vector3":
        return cls(x=t[0], y=t[1], z=t[2])
    
    def distance_to(self, other: "Vector3") -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2) ** 0.5
    
    def lerp(self, other: "Vector3", t: float) -> "Vector3":
        """Linear interpolation between two vectors."""
        return Vector3(
            x=self.x + (other.x - self.x) * t,
            y=self.y + (other.y - self.y) * t,
            z=self.z + (other.z - self.z) * t
        )


@dataclass
class Transform:
    """Spatial transform (position, rotation, scale)."""
    position: Vector3 = field(default_factory=Vector3)
    rotation: Vector3 = field(default_factory=Vector3)  # Euler angles
    scale: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "scale": self.scale.to_dict()
        }


@dataclass
class CharacterState:
    """Character-specific state within scene."""
    emotion: EmotionalState = EmotionalState.NEUTRAL
    emotion_intensity: float = 0.5  # 0.0 - 1.0
    posture: str = "standing"
    action: str = "idle"
    gaze_target: Optional[str] = None  # Entity ID or "camera"
    speaking: bool = False
    expression_details: Dict[str, Any] = field(default_factory=dict)
    
    # Emotional arc tracking
    emotion_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotion": self.emotion.value,
            "emotion_intensity": self.emotion_intensity,
            "posture": self.posture,
            "action": self.action,
            "gaze_target": self.gaze_target,
            "speaking": self.speaking,
            "expression_details": self.expression_details
        }
    
    def transition_emotion(self, new_emotion: EmotionalState, intensity: float = 0.5):
        """Record emotional transition for arc tracking."""
        self.emotion_history.append({
            "from": self.emotion.value,
            "to": new_emotion.value,
            "intensity": intensity
        })
        self.emotion = new_emotion
        self.emotion_intensity = intensity


@dataclass
class Entity:
    """An entity in the scene graph."""
    id: str
    type: EntityType
    transform: Transform = field(default_factory=Transform)
    visible: bool = True
    
    # Type-specific state
    character_state: Optional[CharacterState] = None
    
    # Visual properties
    visual_anchor: Optional[str] = None  # Path to reference image
    style_overrides: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "type": self.type.value,
            "transform": self.transform.to_dict(),
            "visible": self.visible,
            "visual_anchor": self.visual_anchor,
            "style_overrides": self.style_overrides,
            "parent": self.parent,
            "children": self.children,
            "metadata": self.metadata
        }
        if self.character_state:
            d["character_state"] = self.character_state.to_dict()
        return d


@dataclass
class CameraState:
    """Camera state and trajectory."""
    position: Vector3 = field(default_factory=Vector3)
    target: Optional[str] = None  # Entity ID to look at
    target_position: Optional[Vector3] = None  # Or explicit position
    
    # Lens properties
    lens: str = "35mm"
    aperture: str = "f/2.8"
    focal_length: int = 35
    
    # DOF
    focus_distance: float = 5.0
    depth_of_field: str = "medium"  # shallow, medium, deep
    
    # Motion
    motion_type: str = "static"  # static, pan, dolly, crane, handheld
    motion_speed: float = 1.0
    motion_path: List[Vector3] = field(default_factory=list)
    
    # Framing
    framing: str = "center"  # center, rule_of_thirds, leading_space
    shot_type: str = "medium"  # wide, medium, close-up, extreme-close-up
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "target": self.target,
            "target_position": self.target_position.to_dict() if self.target_position else None,
            "lens": self.lens,
            "aperture": self.aperture,
            "focal_length": self.focal_length,
            "focus_distance": self.focus_distance,
            "depth_of_field": self.depth_of_field,
            "motion_type": self.motion_type,
            "motion_speed": self.motion_speed,
            "framing": self.framing,
            "shot_type": self.shot_type
        }


@dataclass
class LightingState:
    """Scene lighting state."""
    time_of_day: str = "day"
    ambient_color: Tuple[int, int, int] = (255, 255, 255)
    ambient_intensity: float = 0.3
    
    # Key light
    key_light_color: Tuple[int, int, int] = (255, 255, 255)
    key_light_intensity: float = 1.0
    key_light_direction: Vector3 = field(default_factory=lambda: Vector3(-1, -1, -1))
    
    # Fill light
    fill_light_intensity: float = 0.5
    
    # Rim/back light
    rim_light_intensity: float = 0.3
    
    # Atmosphere
    fog_density: float = 0.0
    fog_color: Tuple[int, int, int] = (200, 200, 220)
    
    # Color grading
    color_temperature: int = 6500  # Kelvin
    saturation: float = 1.0
    contrast: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_of_day": self.time_of_day,
            "ambient_color": self.ambient_color,
            "ambient_intensity": self.ambient_intensity,
            "key_light_color": self.key_light_color,
            "key_light_intensity": self.key_light_intensity,
            "fill_light_intensity": self.fill_light_intensity,
            "rim_light_intensity": self.rim_light_intensity,
            "fog_density": self.fog_density,
            "color_temperature": self.color_temperature,
            "saturation": self.saturation,
            "contrast": self.contrast
        }
    
    def evolve(self, target: "LightingState", progress: float) -> "LightingState":
        """Interpolate lighting towards a target state."""
        new_state = copy.deepcopy(self)
        new_state.ambient_intensity = self.ambient_intensity + (target.ambient_intensity - self.ambient_intensity) * progress
        new_state.key_light_intensity = self.key_light_intensity + (target.key_light_intensity - self.key_light_intensity) * progress
        new_state.fill_light_intensity = self.fill_light_intensity + (target.fill_light_intensity - self.fill_light_intensity) * progress
        new_state.saturation = self.saturation + (target.saturation - self.saturation) * progress
        new_state.contrast = self.contrast + (target.contrast - self.contrast) * progress
        return new_state


@dataclass
class ConflictRelationship:
    """Tracks dramatic tension between entities."""
    entity_a: str
    entity_b: str
    tension_level: float = 0.0  # -1.0 (ally) to 1.0 (enemy)
    relationship_type: str = "neutral"  # ally, friend, neutral, rival, enemy
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_a": self.entity_a,
            "entity_b": self.entity_b,
            "tension_level": self.tension_level,
            "relationship_type": self.relationship_type,
            "history": self.history
        }


class SceneGraph:
    """
    Full scene graph for cinematic continuity.
    
    Manages all entities, camera, lighting, and relationships
    with support for temporal evolution and snapshots.
    """
    
    def __init__(self, scene_id: str = "scene_001"):
        self.scene_id = scene_id
        self.frame_number = 0
        
        # Core state
        self._entities: Dict[str, Entity] = {}
        self._camera = CameraState()
        self._lighting = LightingState()
        
        # Relationships
        self._conflicts: Dict[str, ConflictRelationship] = {}
        
        # Environment
        self.environment_id: Optional[str] = None
        self.environment_metadata: Dict[str, Any] = {}
        
        # History for continuity
        self._snapshots: List[Dict[str, Any]] = []
        
        # Audio state
        self._active_speaker: Optional[str] = None
        self._last_dialogue: Optional[str] = None
        self._audio_cues: List[Dict[str, Any]] = []
    
    # ============ Entity Management ============
    
    def add_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        position: Optional[Tuple[float, float, float]] = None,
        **kwargs
    ) -> Entity:
        """Add an entity to the scene."""
        transform = Transform()
        if position:
            transform.position = Vector3.from_tuple(position)
        
        entity = Entity(
            id=entity_id,
            type=entity_type,
            transform=transform,
            **kwargs
        )
        
        # Initialize character state for characters
        if entity_type == EntityType.CHARACTER:
            entity.character_state = CharacterState()
        
        self._entities[entity_id] = entity
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self._entities.get(entity_id)
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the scene."""
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False
    
    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update entity properties."""
        if entity_id not in self._entities:
            return False
        
        entity = self._entities[entity_id]
        
        if "position" in updates:
            pos = updates["position"]
            if isinstance(pos, tuple):
                entity.transform.position = Vector3.from_tuple(pos)
            elif isinstance(pos, Vector3):
                entity.transform.position = pos
        
        if "emotion" in updates and entity.character_state:
            emotion = updates["emotion"]
            if isinstance(emotion, str):
                emotion = EmotionalState(emotion)
            intensity = updates.get("emotion_intensity", 0.5)
            entity.character_state.transition_emotion(emotion, intensity)
        
        if "action" in updates and entity.character_state:
            entity.character_state.action = updates["action"]
        
        if "speaking" in updates and entity.character_state:
            entity.character_state.speaking = updates["speaking"]
        
        if "gaze_target" in updates and entity.character_state:
            entity.character_state.gaze_target = updates["gaze_target"]
        
        if "visible" in updates:
            entity.visible = updates["visible"]
        
        return True
    
    def get_characters(self) -> Dict[str, Entity]:
        """Get all character entities."""
        return {
            eid: e for eid, e in self._entities.items()
            if e.type == EntityType.CHARACTER
        }
    
    def get_props(self) -> Dict[str, Entity]:
        """Get all prop entities."""
        return {
            eid: e for eid, e in self._entities.items()
            if e.type == EntityType.PROP
        }
    
    # ============ Camera Management ============
    
    def set_camera(self, camera: CameraState):
        """Set the camera state."""
        self._camera = camera
    
    def update_camera(self, **updates):
        """Update camera properties."""
        if "position" in updates:
            pos = updates["position"]
            if isinstance(pos, tuple):
                self._camera.position = Vector3.from_tuple(pos)
            elif isinstance(pos, Vector3):
                self._camera.position = pos
        
        for key in ["target", "lens", "aperture", "motion_type", "framing", "shot_type"]:
            if key in updates:
                setattr(self._camera, key, updates[key])
    
    @property
    def camera(self) -> CameraState:
        return self._camera
    
    # ============ Lighting Management ============
    
    def set_lighting(self, lighting: LightingState):
        """Set the lighting state."""
        self._lighting = lighting
    
    def evolve_lighting(self, target: LightingState, progress: float):
        """Evolve lighting towards target state."""
        self._lighting = self._lighting.evolve(target, progress)
    
    @property
    def lighting(self) -> LightingState:
        return self._lighting
    
    # ============ Conflict/Relationship Management ============
    
    def set_relationship(
        self,
        entity_a: str,
        entity_b: str,
        tension: float = 0.0,
        relationship_type: str = "neutral"
    ):
        """Set or update a relationship between entities."""
        key = f"{min(entity_a, entity_b)}:{max(entity_a, entity_b)}"
        
        if key in self._conflicts:
            rel = self._conflicts[key]
            rel.history.append({
                "frame": self.frame_number,
                "old_tension": rel.tension_level,
                "new_tension": tension
            })
            rel.tension_level = tension
            rel.relationship_type = relationship_type
        else:
            self._conflicts[key] = ConflictRelationship(
                entity_a=entity_a,
                entity_b=entity_b,
                tension_level=tension,
                relationship_type=relationship_type
            )
    
    def get_relationship(self, entity_a: str, entity_b: str) -> Optional[ConflictRelationship]:
        """Get relationship between two entities."""
        key = f"{min(entity_a, entity_b)}:{max(entity_a, entity_b)}"
        return self._conflicts.get(key)
    
    def get_dramatic_peak_entities(self, threshold: float = 0.7) -> List[Tuple[str, str]]:
        """Get entity pairs with high dramatic tension."""
        return [
            (rel.entity_a, rel.entity_b)
            for rel in self._conflicts.values()
            if abs(rel.tension_level) >= threshold
        ]
    
    # ============ Audio State ============
    
    def set_speaker(self, entity_id: Optional[str], dialogue: Optional[str] = None):
        """Set the active speaker."""
        self._active_speaker = entity_id
        self._last_dialogue = dialogue
        
        # Update entity speaking state
        for eid, entity in self._entities.items():
            if entity.character_state:
                entity.character_state.speaking = (eid == entity_id)
    
    def add_audio_cue(self, cue_type: str, **metadata):
        """Add an audio cue (music, sfx, etc.)."""
        self._audio_cues.append({
            "frame": self.frame_number,
            "type": cue_type,
            **metadata
        })
    
    # ============ Snapshot & History ============
    
    def take_snapshot(self) -> Dict[str, Any]:
        """Capture current state as a snapshot."""
        snapshot = {
            "scene_id": self.scene_id,
            "frame_number": self.frame_number,
            "entities": {eid: e.to_dict() for eid, e in self._entities.items()},
            "camera": self._camera.to_dict(),
            "lighting": self._lighting.to_dict(),
            "conflicts": {k: v.to_dict() for k, v in self._conflicts.items()},
            "environment_id": self.environment_id,
            "environment_metadata": self.environment_metadata,
            "active_speaker": self._active_speaker,
            "last_dialogue": self._last_dialogue,
            "audio_cues": self._audio_cues.copy()
        }
        self._snapshots.append(copy.deepcopy(snapshot))
        return snapshot
    
    def advance_frame(self, duration_frames: int = 1):
        """Advance the scene by N frames, taking snapshot."""
        self.take_snapshot()
        self.frame_number += duration_frames
    
    def get_continuity_context(self, lookback: int = 3) -> Dict[str, Any]:
        """
        Get context from recent frames for continuity.
        
        Returns structured data for AI prompt generation.
        """
        if not self._snapshots:
            return {}
        
        recent = self._snapshots[-lookback:] if len(self._snapshots) >= lookback else self._snapshots
        
        # Character emotional arcs
        character_arcs = {}
        for char_id, entity in self.get_characters().items():
            if entity.character_state:
                character_arcs[char_id] = {
                    "current_emotion": entity.character_state.emotion.value,
                    "intensity": entity.character_state.emotion_intensity,
                    "recent_history": entity.character_state.emotion_history[-3:],
                    "current_action": entity.character_state.action,
                    "position": entity.transform.position.to_tuple()
                }
        
        # Camera trajectory
        camera_trajectory = [
            s["camera"]["position"] for s in recent
        ]
        
        # Lighting evolution
        lighting_history = [
            {
                "ambient": s["lighting"]["ambient_intensity"],
                "key": s["lighting"]["key_light_intensity"],
                "saturation": s["lighting"]["saturation"]
            }
            for s in recent
        ]
        
        # Active conflicts
        active_conflicts = [
            {
                "entities": (rel.entity_a, rel.entity_b),
                "tension": rel.tension_level,
                "type": rel.relationship_type
            }
            for rel in self._conflicts.values()
            if abs(rel.tension_level) > 0.3
        ]
        
        return {
            "frame_number": self.frame_number,
            "character_arcs": character_arcs,
            "camera_trajectory": camera_trajectory,
            "lighting_evolution": lighting_history,
            "active_conflicts": active_conflicts,
            "last_speaker": self._active_speaker,
            "last_dialogue": self._last_dialogue,
            "recent_audio_cues": [c for c in self._audio_cues if c["frame"] >= self.frame_number - 100]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export full scene graph to dict."""
        return self.take_snapshot()
    
    def to_json(self, path: Optional[str] = None) -> str:
        """Export to JSON."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)
        
        if path:
            Path(path).write_text(json_str)
        
        return json_str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneGraph":
        """Create scene graph from dict."""
        graph = cls(scene_id=data.get("scene_id", "scene_001"))
        graph.frame_number = data.get("frame_number", 0)
        graph.environment_id = data.get("environment_id")
        graph.environment_metadata = data.get("environment_metadata", {})
        
        # Restore entities
        for eid, edata in data.get("entities", {}).items():
            entity = Entity(
                id=eid,
                type=EntityType(edata["type"]),
                transform=Transform(
                    position=Vector3(**edata["transform"]["position"]),
                    rotation=Vector3(**edata["transform"]["rotation"]),
                    scale=Vector3(**edata["transform"]["scale"])
                ),
                visible=edata.get("visible", True),
                visual_anchor=edata.get("visual_anchor"),
                style_overrides=edata.get("style_overrides", {}),
                metadata=edata.get("metadata", {})
            )
            
            if "character_state" in edata:
                cs = edata["character_state"]
                entity.character_state = CharacterState(
                    emotion=EmotionalState(cs.get("emotion", "neutral")),
                    emotion_intensity=cs.get("emotion_intensity", 0.5),
                    posture=cs.get("posture", "standing"),
                    action=cs.get("action", "idle"),
                    gaze_target=cs.get("gaze_target"),
                    speaking=cs.get("speaking", False)
                )
            
            graph._entities[eid] = entity
        
        return graph
    
    @classmethod
    def from_json(cls, path_or_str: str) -> "SceneGraph":
        """Load from JSON file or string."""
        if Path(path_or_str).exists():
            data = json.loads(Path(path_or_str).read_text())
        else:
            data = json.loads(path_or_str)
        return cls.from_dict(data)
