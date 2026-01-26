"""
JSON Shot Plan System
=====================
Structured shot planning with full metadata for reproducible video generation.

Features:
- Complete shot specification in JSON
- Scene/shot hierarchy
- Cinematography metadata per shot
- Character and environment states
- Audio cues and timing
- Provider selection per shot

Example:
    from ministudio.shot_plan import ShotPlan, Shot, load_shot_plan
    
    plan = ShotPlan.create("My Video")
    plan.add_shot(Shot(
        action="Emma walks into the lab",
        duration=5,
        camera=CameraSpec(lens="35mm", motion="dolly_in"),
        characters={"emma": CharacterSpec(emotion="curious")}
    ))
    
    plan.save("my_video_plan.json")
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from datetime import datetime


class ShotType(Enum):
    """Standard shot types."""
    EXTREME_WIDE = "extreme_wide"
    WIDE = "wide"
    FULL = "full"
    MEDIUM_WIDE = "medium_wide"
    MEDIUM = "medium"
    MEDIUM_CLOSE = "medium_close"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    INSERT = "insert"
    POV = "pov"
    OVER_SHOULDER = "over_shoulder"
    TWO_SHOT = "two_shot"


class CameraMotion(Enum):
    """Camera motion types."""
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    DOLLY_LEFT = "dolly_left"
    DOLLY_RIGHT = "dolly_right"
    CRANE_UP = "crane_up"
    CRANE_DOWN = "crane_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    HANDHELD = "handheld"
    TRACKING = "tracking"
    ARC_LEFT = "arc_left"
    ARC_RIGHT = "arc_right"
    STEADICAM = "steadicam"


class Transition(Enum):
    """Shot transitions."""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    MATCH_CUT = "match_cut"
    JUMP_CUT = "jump_cut"
    CROSS_FADE = "cross_fade"


@dataclass
class CameraSpec:
    """Camera specification for a shot."""
    lens: str = "35mm"
    aperture: str = "f/2.8"
    focal_length: int = 35
    motion: Union[str, CameraMotion] = CameraMotion.STATIC
    motion_speed: float = 1.0  # Relative speed
    
    # Framing
    framing: str = "rule_of_thirds"  # center, rule_of_thirds, golden_ratio, leading_space
    shot_type: Union[str, ShotType] = ShotType.MEDIUM
    
    # DOF
    depth_of_field: str = "medium"  # shallow, medium, deep
    focus_target: Optional[str] = None  # Entity ID to focus on
    focus_pull: bool = False  # Whether to pull focus during shot
    
    # Position (optional - can be inferred)
    position: Optional[Dict[str, float]] = None  # {"x": 0, "y": 0, "z": -5}
    target: Optional[str] = None  # Entity ID to look at
    
    # Depth layers for prompt
    depth_layers: List[str] = field(default_factory=lambda: ["foreground", "midground", "background"])
    
    def to_dict(self) -> Dict[str, Any]:
        d = {
            "lens": self.lens,
            "aperture": self.aperture,
            "focal_length": self.focal_length,
            "motion": self.motion.value if isinstance(self.motion, CameraMotion) else self.motion,
            "motion_speed": self.motion_speed,
            "framing": self.framing,
            "shot_type": self.shot_type.value if isinstance(self.shot_type, ShotType) else self.shot_type,
            "depth_of_field": self.depth_of_field,
            "focus_target": self.focus_target,
            "focus_pull": self.focus_pull,
            "depth_layers": self.depth_layers
        }
        if self.position:
            d["position"] = self.position
        if self.target:
            d["target"] = self.target
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CameraSpec":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class LightingSpec:
    """Lighting specification for a shot."""
    time_of_day: str = "day"  # dawn, morning, day, afternoon, golden_hour, dusk, night
    mood: str = "neutral"  # dramatic, soft, harsh, mysterious, romantic, etc.
    
    # Key light
    key_direction: str = "front_left"  # front, front_left, front_right, side, back, etc.
    key_intensity: float = 1.0
    key_color_temp: int = 5600  # Kelvin
    
    # Fill
    fill_ratio: float = 0.5  # Fill relative to key (0.5 = half as bright)
    
    # Rim/back
    rim_intensity: float = 0.3
    
    # Atmosphere
    fog: bool = False
    fog_density: float = 0.0
    particles: bool = False  # Dust, rain, etc.
    particle_type: Optional[str] = None
    
    # Color grading hints
    color_grade: str = "neutral"  # neutral, warm, cool, vintage, cinematic, etc.
    saturation: float = 1.0
    contrast: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LightingSpec":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CharacterSpec:
    """Character state for a shot."""
    emotion: str = "neutral"
    emotion_intensity: float = 0.5
    action: str = "standing"
    posture: str = "relaxed"
    gaze_target: Optional[str] = None  # Entity ID, "camera", or None
    speaking: bool = False
    
    # Position override (relative to scene)
    position: Optional[Dict[str, float]] = None
    
    # Costume/appearance override for this shot
    costume: Optional[str] = None
    props: List[str] = field(default_factory=list)
    
    # Reference for grounding
    visual_anchor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = {
            "emotion": self.emotion,
            "emotion_intensity": self.emotion_intensity,
            "action": self.action,
            "posture": self.posture,
            "speaking": self.speaking
        }
        if self.gaze_target:
            d["gaze_target"] = self.gaze_target
        if self.position:
            d["position"] = self.position
        if self.costume:
            d["costume"] = self.costume
        if self.props:
            d["props"] = self.props
        if self.visual_anchor:
            d["visual_anchor"] = self.visual_anchor
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterSpec":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass 
class EnvironmentSpec:
    """Environment state for a shot."""
    location: str = ""
    weather: str = "clear"
    time_of_day: str = "day"
    
    # Dynamic elements
    dynamic_elements: List[str] = field(default_factory=list)  # Moving elements
    
    # Reference images
    reference_images: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentSpec":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AudioSpec:
    """Audio specification for a shot."""
    # Narration
    narration: Optional[str] = None
    narration_voice: Optional[str] = None
    narration_style: str = "narrative"
    
    # Dialogue
    dialogue: Optional[str] = None  # "Character: line"
    dialogue_emotion: str = "neutral"
    
    # Voice settings
    pitch: float = 1.0
    speed: float = 1.0
    
    # Music cues
    music_cue: Optional[str] = None  # Track ID or description
    music_action: str = "continue"  # start, continue, stop, fade_in, fade_out
    music_intensity: float = 0.5
    
    # SFX
    sound_effects: List[str] = field(default_factory=list)
    
    # Timing
    audio_delay: float = 0.0  # Delay audio start (seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.narration:
            d["narration"] = {
                "text": self.narration,
                "voice": self.narration_voice,
                "style": self.narration_style,
                "pitch": self.pitch,
                "speed": self.speed
            }
        if self.dialogue:
            d["dialogue"] = {
                "text": self.dialogue,
                "emotion": self.dialogue_emotion,
                "pitch": self.pitch,
                "speed": self.speed
            }
        if self.music_cue:
            d["music"] = {
                "cue": self.music_cue,
                "action": self.music_action,
                "intensity": self.music_intensity
            }
        if self.sound_effects:
            d["sfx"] = self.sound_effects
        if self.audio_delay:
            d["delay"] = self.audio_delay
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioSpec":
        spec = cls()
        if "narration" in data:
            n = data["narration"]
            spec.narration = n.get("text")
            spec.narration_voice = n.get("voice")
            spec.narration_style = n.get("style", "narrative")
            spec.pitch = n.get("pitch", 1.0)
            spec.speed = n.get("speed", 1.0)
        if "dialogue" in data:
            d = data["dialogue"]
            spec.dialogue = d.get("text")
            spec.dialogue_emotion = d.get("emotion", "neutral")
        if "music" in data:
            m = data["music"]
            spec.music_cue = m.get("cue")
            spec.music_action = m.get("action", "continue")
            spec.music_intensity = m.get("intensity", 0.5)
        if "sfx" in data:
            spec.sound_effects = data["sfx"]
        if "delay" in data:
            spec.audio_delay = data["delay"]
        return spec


@dataclass
class EffectsSpec:
    """Visual effects for a shot."""
    lens_flare: bool = False
    motion_blur: bool = False
    film_grain: float = 0.0  # 0.0 - 1.0
    vignette: float = 0.0
    
    # Overlays
    overlays: List[str] = field(default_factory=list)  # Particle effects, UI elements, etc.
    
    # Speed
    slow_motion: bool = False
    slow_motion_factor: float = 0.5
    time_lapse: bool = False
    time_lapse_factor: float = 2.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EffectsSpec":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Shot:
    """Complete shot specification."""
    # Identity
    shot_id: str = field(default_factory=lambda: f"shot_{uuid.uuid4().hex[:8]}")
    scene_id: str = ""
    order: int = 0
    
    # Core content
    action: str = ""  # What happens in this shot
    description: str = ""  # Additional description/context
    
    # Timing
    duration: Optional[float] = None  # None = auto from audio
    min_duration: float = 3.0
    max_duration: float = 8.0
    
    # Transition
    transition_in: Transition = Transition.CUT
    transition_out: Transition = Transition.CUT
    transition_duration: float = 0.5
    
    # Components
    camera: CameraSpec = field(default_factory=CameraSpec)
    lighting: LightingSpec = field(default_factory=LightingSpec)
    characters: Dict[str, CharacterSpec] = field(default_factory=dict)
    environment: Optional[EnvironmentSpec] = None
    audio: AudioSpec = field(default_factory=AudioSpec)
    effects: EffectsSpec = field(default_factory=EffectsSpec)
    
    # Provider selection
    provider: Optional[str] = None  # Override provider for this shot
    provider_config: Dict[str, Any] = field(default_factory=dict)
    
    # Continuity
    continuity_required: bool = True
    starting_frame: Optional[str] = None  # Path to starting frame
    
    # Generation metadata
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    
    # Results (filled after generation)
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "shot_id": self.shot_id,
            "scene_id": self.scene_id,
            "order": self.order,
            "action": self.action,
            "description": self.description,
            "duration": self.duration,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "transition_in": self.transition_in.value if isinstance(self.transition_in, Transition) else self.transition_in,
            "transition_out": self.transition_out.value if isinstance(self.transition_out, Transition) else self.transition_out,
            "transition_duration": self.transition_duration,
            "camera": self.camera.to_dict(),
            "lighting": self.lighting.to_dict(),
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "environment": self.environment.to_dict() if self.environment else None,
            "audio": self.audio.to_dict(),
            "effects": self.effects.to_dict(),
            "provider": self.provider,
            "provider_config": self.provider_config,
            "continuity_required": self.continuity_required,
            "starting_frame": self.starting_frame,
            "negative_prompt": self.negative_prompt,
            "seed": self.seed,
            "video_path": self.video_path,
            "audio_path": self.audio_path,
            "generation_metadata": self.generation_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shot":
        shot = cls(
            shot_id=data.get("shot_id", f"shot_{uuid.uuid4().hex[:8]}"),
            scene_id=data.get("scene_id", ""),
            order=data.get("order", 0),
            action=data.get("action", ""),
            description=data.get("description", ""),
            duration=data.get("duration"),
            min_duration=data.get("min_duration", 3.0),
            max_duration=data.get("max_duration", 8.0),
            transition_in=Transition(data.get("transition_in", "cut")),
            transition_out=Transition(data.get("transition_out", "cut")),
            transition_duration=data.get("transition_duration", 0.5),
            provider=data.get("provider"),
            provider_config=data.get("provider_config", {}),
            continuity_required=data.get("continuity_required", True),
            starting_frame=data.get("starting_frame"),
            negative_prompt=data.get("negative_prompt"),
            seed=data.get("seed"),
            video_path=data.get("video_path"),
            audio_path=data.get("audio_path"),
            generation_metadata=data.get("generation_metadata", {})
        )
        
        if "camera" in data:
            shot.camera = CameraSpec.from_dict(data["camera"])
        if "lighting" in data:
            shot.lighting = LightingSpec.from_dict(data["lighting"])
        if "characters" in data:
            shot.characters = {k: CharacterSpec.from_dict(v) for k, v in data["characters"].items()}
        if "environment" in data and data["environment"]:
            shot.environment = EnvironmentSpec.from_dict(data["environment"])
        if "audio" in data:
            shot.audio = AudioSpec.from_dict(data["audio"])
        if "effects" in data:
            shot.effects = EffectsSpec.from_dict(data["effects"])
        
        return shot


@dataclass
class Scene:
    """A scene containing multiple shots."""
    scene_id: str = field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    
    # Environment (default for all shots in scene)
    environment: Optional[EnvironmentSpec] = None
    
    # Characters in scene (default states)
    characters: Dict[str, CharacterSpec] = field(default_factory=dict)
    
    # Lighting (default for scene)
    lighting: LightingSpec = field(default_factory=LightingSpec)
    
    # Shots
    shots: List[Shot] = field(default_factory=list)
    
    # Scene-level metadata
    mood: str = "neutral"
    style: str = "cinematic"
    
    def add_shot(self, shot: Shot) -> Shot:
        """Add a shot to the scene."""
        shot.scene_id = self.scene_id
        shot.order = len(self.shots)
        
        # Inherit scene defaults if not specified
        if shot.environment is None and self.environment:
            shot.environment = self.environment
        
        # Merge character defaults
        for char_id, char_spec in self.characters.items():
            if char_id not in shot.characters:
                shot.characters[char_id] = char_spec
        
        self.shots.append(shot)
        return shot
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "description": self.description,
            "environment": self.environment.to_dict() if self.environment else None,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "lighting": self.lighting.to_dict(),
            "shots": [s.to_dict() for s in self.shots],
            "mood": self.mood,
            "style": self.style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        scene = cls(
            scene_id=data.get("scene_id", f"scene_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            mood=data.get("mood", "neutral"),
            style=data.get("style", "cinematic")
        )
        
        if "environment" in data and data["environment"]:
            scene.environment = EnvironmentSpec.from_dict(data["environment"])
        if "characters" in data:
            scene.characters = {k: CharacterSpec.from_dict(v) for k, v in data["characters"].items()}
        if "lighting" in data:
            scene.lighting = LightingSpec.from_dict(data["lighting"])
        if "shots" in data:
            scene.shots = [Shot.from_dict(s) for s in data["shots"]]
        
        return scene


@dataclass
class CharacterDefinition:
    """Character definition for the production."""
    character_id: str
    name: str
    description: str = ""
    
    # Identity (persistent across shots)
    identity: Dict[str, str] = field(default_factory=dict)  # hair, eyes, skin, etc.
    
    # Visual anchors
    reference_images: List[str] = field(default_factory=list)
    visual_anchor: Optional[str] = None
    
    # Voice
    voice_id: Optional[str] = None
    voice_profile: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterDefinition":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ShotPlan:
    """Complete shot plan for a video production."""
    # Identity
    plan_id: str = field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    
    # Global settings
    default_provider: Optional[str] = None
    aspect_ratio: str = "16:9"
    resolution: str = "1080p"
    frame_rate: int = 24
    
    # Characters
    characters: Dict[str, CharacterDefinition] = field(default_factory=dict)
    
    # Scenes
    scenes: List[Scene] = field(default_factory=list)
    
    # Style
    global_style: str = "cinematic"
    style_references: List[str] = field(default_factory=list)
    negative_prompt: Optional[str] = None
    
    # Output
    output_dir: str = "./output"
    output_filename: Optional[str] = None
    
    @classmethod
    def create(cls, title: str, **kwargs) -> "ShotPlan":
        """Create a new shot plan."""
        return cls(title=title, **kwargs)
    
    def add_character(
        self,
        character_id: str,
        name: str,
        **kwargs
    ) -> CharacterDefinition:
        """Add a character definition."""
        char = CharacterDefinition(
            character_id=character_id,
            name=name,
            **kwargs
        )
        self.characters[character_id] = char
        return char
    
    def add_scene(self, scene: Scene) -> Scene:
        """Add a scene to the plan."""
        self.scenes.append(scene)
        return scene
    
    def create_scene(self, name: str, **kwargs) -> Scene:
        """Create and add a new scene."""
        scene = Scene(name=name, **kwargs)
        return self.add_scene(scene)
    
    def add_shot(
        self,
        shot: Shot,
        scene_index: int = -1
    ) -> Shot:
        """Add a shot to a scene (default: last scene)."""
        if not self.scenes:
            self.create_scene("Scene 1")
        
        target_scene = self.scenes[scene_index]
        return target_scene.add_shot(shot)
    
    def get_all_shots(self) -> List[Shot]:
        """Get all shots in order."""
        shots = []
        for scene in self.scenes:
            shots.extend(scene.shots)
        return shots
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "default_provider": self.default_provider,
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
            "frame_rate": self.frame_rate,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "scenes": [s.to_dict() for s in self.scenes],
            "global_style": self.global_style,
            "style_references": self.style_references,
            "negative_prompt": self.negative_prompt,
            "output_dir": self.output_dir,
            "output_filename": self.output_filename
        }
    
    def to_json(self, pretty: bool = True) -> str:
        """Export to JSON string."""
        return json.dumps(self.to_dict(), indent=2 if pretty else None)
    
    def save(self, path: Union[str, Path]):
        """Save to JSON file."""
        path = Path(path)
        path.write_text(self.to_json())
        self.updated_at = datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShotPlan":
        """Create from dictionary."""
        plan = cls(
            plan_id=data.get("plan_id", f"plan_{uuid.uuid4().hex[:8]}"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            version=data.get("version", "1.0.0"),
            default_provider=data.get("default_provider"),
            aspect_ratio=data.get("aspect_ratio", "16:9"),
            resolution=data.get("resolution", "1080p"),
            frame_rate=data.get("frame_rate", 24),
            global_style=data.get("global_style", "cinematic"),
            style_references=data.get("style_references", []),
            negative_prompt=data.get("negative_prompt"),
            output_dir=data.get("output_dir", "./output"),
            output_filename=data.get("output_filename")
        )
        
        if "characters" in data:
            plan.characters = {
                k: CharacterDefinition.from_dict(v) 
                for k, v in data["characters"].items()
            }
        
        if "scenes" in data:
            plan.scenes = [Scene.from_dict(s) for s in data["scenes"]]
        
        return plan
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> "ShotPlan":
        """Load from JSON file."""
        path = Path(path)
        data = json.loads(path.read_text())
        return cls.from_dict(data)


def load_shot_plan(path: Union[str, Path]) -> ShotPlan:
    """Load a shot plan from file."""
    return ShotPlan.load(path)


def create_shot_plan(title: str, **kwargs) -> ShotPlan:
    """Create a new shot plan."""
    return ShotPlan.create(title, **kwargs)


# ============ Shot Progression Templates ============

def create_standard_progression(
    subject: str,
    action: str,
    duration: float = 20.0
) -> List[Shot]:
    """
    Create a standard cinematic progression:
    Wide Establishing → Medium → Close-Up → (optional) ECU → Medium/Wide resolution
    """
    shot_duration = duration / 4
    
    return [
        Shot(
            action=f"Wide establishing shot of {subject}",
            duration=shot_duration,
            camera=CameraSpec(
                shot_type=ShotType.WIDE,
                lens="24mm",
                motion=CameraMotion.STATIC
            )
        ),
        Shot(
            action=f"Medium shot: {action}",
            duration=shot_duration,
            camera=CameraSpec(
                shot_type=ShotType.MEDIUM,
                lens="35mm",
                motion=CameraMotion.DOLLY_IN
            ),
            transition_in=Transition.CUT
        ),
        Shot(
            action=f"Close-up on {subject}'s reaction",
            duration=shot_duration,
            camera=CameraSpec(
                shot_type=ShotType.CLOSE_UP,
                lens="50mm",
                depth_of_field="shallow"
            ),
            transition_in=Transition.CUT
        ),
        Shot(
            action=f"Resolution: {subject} continues",
            duration=shot_duration,
            camera=CameraSpec(
                shot_type=ShotType.MEDIUM,
                lens="35mm",
                motion=CameraMotion.DOLLY_OUT
            ),
            transition_in=Transition.CUT
        )
    ]


def create_dialogue_coverage(
    character_a: str,
    character_b: str,
    dialogue_lines: List[Tuple[str, str]]  # [(speaker, line), ...]
) -> List[Shot]:
    """
    Create standard dialogue coverage:
    Two-shot → Over-shoulder A → Over-shoulder B → etc.
    """
    shots = []
    
    # Opening two-shot
    shots.append(Shot(
        action=f"Two-shot of {character_a} and {character_b}",
        duration=3.0,
        camera=CameraSpec(
            shot_type=ShotType.TWO_SHOT,
            lens="35mm"
        )
    ))
    
    # Coverage for each line
    for speaker, line in dialogue_lines:
        target = character_a if speaker == character_a else character_b
        other = character_b if speaker == character_a else character_a
        
        shots.append(Shot(
            action=f"Over-shoulder shot on {target}",
            camera=CameraSpec(
                shot_type=ShotType.OVER_SHOULDER,
                lens="50mm",
                focus_target=target
            ),
            characters={
                target: CharacterSpec(
                    speaking=True,
                    gaze_target=other
                )
            },
            audio=AudioSpec(
                dialogue=f"{speaker}: {line}"
            )
        ))
    
    return shots
