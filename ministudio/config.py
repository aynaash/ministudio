"""
Configuration system for Ministudio video generation.
Supports "Code-as-Video" programmatic visual specifications.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Union, List, Tuple
from pathlib import Path
import json

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# --- Helper Types ---

@dataclass
class Color:
    """Color representation supporting hex or HSL"""
    hex: Optional[str] = None
    hsl: Optional[Tuple[int, int, int]] = None

    def __str__(self):
        if self.hsl:
            return f"HSL{self.hsl}"
        return self.hex or "unknown_color"

    def to_dict(self):
        return {"hex": self.hex, "hsl": self.hsl}


@dataclass
class Vector3:
    x: float
    y: float
    z: float

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}


class ShotType(str, Enum):
    WS = "Wide Shot"
    MS = "Medium Shot"
    CU = "Close-Up"
    ECU = "Extreme Close-Up"


@dataclass
class VoiceProfile:
    """Detailed voice characteristics"""
    gender: str = "neutral"
    style: str = "warm"  # warm, husky, energetic, robotic, etc.
    accent: Optional[str] = None
    pitch: float = 1.0
    stability: float = 0.5

    def to_dict(self):
        return asdict(self)

# --- 1. Character DNA ---


@dataclass
class ParticleSystem:
    emission_rate: float
    colors: List[Color]
    motion: str  # e.g. "spiral_outward"


@dataclass
class Character:
    """Genetics and behavioral programming for a character"""
    name: str = "unknown"

    # GLOBAL IDENTITY (Static across scenes)
    identity: Dict[str, Any] = field(default_factory=lambda: {
        "hair_style": "",
        "hair_color": "",
        "eye_color": "",
        "skin_tone": "",
        "face_shape": "",
        "height_build": ""
    })

    # LOCAL STATE (Changes per scene/shot)
    current_state: Dict[str, Any] = field(default_factory=lambda: {
        "clothing": "",
        "equipment": "",
        "emotion": "neutral",
        "posture": ""
    })

    # Legacy/Extended genetics (merged into identity for compilation)
    genetics: Dict[str, Any] = field(default_factory=dict)
    motion_library: Dict[str, str] = field(default_factory=dict)
    emotional_palette: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # VISUAL ANCHORS (Reference images for identity grounding)
    reference_images: List[str] = field(default_factory=list)
    # Path to a "Master Close-up" for identity grounding
    visual_anchor_path: Optional[str] = None

    voice_id: Optional[str] = None  # ID for ElevenLabs/Google TTS
    voice_profile: Optional[VoiceProfile] = None

    def to_dict(self):
        return asdict(self)

# --- 2. Environment Engineering ---


@dataclass
class Environment:
    """Physics and world rules"""
    location: str = "void"

    # GLOBAL IDENTITY (Base architecture)
    identity: Dict[str, Any] = field(default_factory=lambda: {
        "architecture_style": "",
        "fixed_elements": "",
        "base_color_palette": ""
    })

    # LOCAL STATE (Lighting, weather, dynamic props)
    current_context: Dict[str, Any] = field(default_factory=lambda: {
        "lighting": "",
        "weather": "",
        "dynamic_props": "",
        "time_of_day": ""
    })

    physics: Dict[str, Any] = field(default_factory=dict)
    generation_rules: Dict[str, Any] = field(default_factory=dict)
    composition: Dict[str, Any] = field(default_factory=dict)
    reference_images: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

# --- 3. Cinematography ---


@dataclass
class Camera:
    lens: str = "35mm"
    aperture: str = "f/2.8"
    focal_length: int = 35
    movement_style: str = "static"
    focus_pulling: str = "auto"


@dataclass
class Persona:
    """AI Personality and expertise instructions"""
    name: str = "Assistant"
    description: str = ""
    expertise: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Cinematography:
    """Camera direction and shot composition"""
    camera_behaviors: Dict[str, Camera] = field(default_factory=dict)
    shot_composition_rules: Dict[str, Any] = field(default_factory=dict)
    active_camera: str = "default"

    def to_dict(self):
        return asdict(self)


@dataclass
class ShotConfig:
    """Configuration for a specific shot within a scene"""
    shot_type: ShotType = ShotType.MS
    action: str = ""
    camera_movement: str = "static"
    continuity_required: bool = True
    # Set to None for auto-calculation based on narration
    duration_seconds: Optional[int] = 4

    # Programmable Cuts: Overrides for this specific shot
    characters: Optional[Dict[str, Character]] = None
    environment: Optional[Environment] = None

    # Audio/Dialogue
    dialogue: Optional[str] = None
    narration: Optional[str] = None
    acting_notes: Optional[str] = None

    def to_dict(self):
        d = {
            "shot_type": self.shot_type.value if isinstance(self.shot_type, ShotType) else self.shot_type,
            "action": self.action,
            "camera_movement": self.camera_movement,
            "continuity_required": self.continuity_required,
            "duration_seconds": self.duration_seconds
        }
        if self.characters:
            d["characters"] = {k: v.to_dict()
                               for k, v in self.characters.items()}
        if self.environment:
            d["environment"] = self.environment.to_dict()
        return d


@dataclass
class SceneConfig:
    """Configuration for a full cinematic scene"""
    concept: str = ""
    characters: Dict[str, Character] = field(default_factory=dict)
    environment: Optional[Environment] = None
    shots: List[ShotConfig] = field(default_factory=list)
    mood: str = "magical"

    # Conflict/Relationship state
    # e.g. {"Captain,Officer": "tense", "Captain,Merchant": "friendly"}
    conflict_matrix: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return {
            "concept": self.concept,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "environment": self.environment.to_dict() if self.environment else None,
            "shots": [s.to_dict() for s in self.shots],
            "mood": self.mood
        }

# --- 4. Lighting ---


@dataclass
class LightSource:
    type: str  # directional, ambient, spot
    color: Color
    intensity: float
    # horizontal, vertical angle
    direction: Optional[Tuple[float, float]] = None
    position: Optional[str] = None
    casts_shadows: bool = False
    shadow_softness: float = 0.5
    angle: Optional[float] = None  # spot angle


@dataclass
class LightingDirector:
    """Lighting program"""
    key_lights: List[LightSource] = field(default_factory=list)
    fill_lights: List[LightSource] = field(default_factory=list)
    rim_lights: List[LightSource] = field(default_factory=list)
    atmosphere: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

# --- 5. Visual Style DNA ---


@dataclass
class StyleDNA:
    """Artistic genetics"""
    traits: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

# --- 6. Continuity ---


@dataclass
class ContinuityEngine:
    """Rules for state persistence"""
    rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

# --- Main Config ---


@dataclass
class VideoConfig:
    """
    Configuration for programmable video generation.
    Supports both legacy flat fields and new hierarchical DNA.
    """

    # Core generation parameters
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    mood: str = "magical"

    # Style and template
    style_name: Optional[str] = "ghibli"
    template_name: Optional[str] = None

    # Prompt customization
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    # Provider settings
    provider_name: str = "mock"
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)

    # Output settings
    output_dir: Union[str, Path] = "./ministudio_output"
    filename_template: str = "{concept}_{timestamp}.mp4"

    # Advanced parameters
    guidance_scale: float = 7.5
    num_inference_steps: int = 20
    enable_safety_checker: bool = True

    # Custom parameters
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    # Persona / Actor Profile
    persona: Optional[Persona] = None

    # --- Programmable "Code-as-Video" Components ---
    characters: Dict[str, Character] = field(default_factory=dict)
    environment: Optional[Environment] = None
    cinematography: Optional[Cinematography] = None
    lighting: Optional[LightingDirector] = None
    style_dna: Optional[StyleDNA] = None
    continuity: Optional[ContinuityEngine] = None

    action_description: str = ""
    conflict_matrix: Dict[str, str] = field(default_factory=dict)

    # Legacy compatibility
    technical: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoConfig':
        """Create config from dictionary"""
        d = data.copy()

        # Hydrate Character objects
        if 'characters' in d and isinstance(d['characters'], dict):
            chars = {}
            for k, v in d['characters'].items():
                if isinstance(v, Character):
                    # Already a Character object
                    chars[k] = v
                elif isinstance(v, dict):
                    # Dict that needs to be hydrated
                    chars[k] = Character(name=k, **v)
                else:
                    chars[k] = v
            d['characters'] = chars

        # Hydrate other objects
        if 'environment' in d and isinstance(d['environment'], dict) and not isinstance(d['environment'], Environment):
            d['environment'] = Environment(**d['environment'])

        if 'cinematography' in d and isinstance(d['cinematography'], dict):
            cine_data = d['cinematography'].copy()
            if 'camera_behaviors' in cine_data:
                cams = {}
                for k, v in cine_data['camera_behaviors'].items():
                    cams[k] = Camera(**v) if isinstance(v, dict) else v
                cine_data['camera_behaviors'] = cams
            d['cinematography'] = Cinematography(**cine_data)

        if 'lighting' in d and isinstance(d['lighting'], dict):
            lighting_data = d['lighting'].copy()
            for key in ['key_lights', 'fill_lights', 'rim_lights']:
                if key in lighting_data and isinstance(lighting_data[key], list):
                    lights = []
                    for l in lighting_data[key]:
                        if isinstance(l, dict):
                            if 'color' in l and isinstance(l['color'], dict):
                                l['color'] = Color(**l['color'])
                            lights.append(LightSource(**l))
                        else:
                            lights.append(l)
                    lighting_data[key] = lights
            d['lighting'] = LightingDirector(**lighting_data)

        if 'style_dna' in d and isinstance(d['style_dna'], dict):
            d['style_dna'] = StyleDNA(**d['style_dna'])

        if 'continuity' in d and isinstance(d['continuity'], dict):
            d['continuity'] = ContinuityEngine(**d['continuity'])

        if 'persona' in d and isinstance(d['persona'], dict):
            d['persona'] = Persona(**d['persona'])

        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> 'VideoConfig':
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'VideoConfig':
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML support")
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        base = {
            'duration_seconds': self.duration_seconds,
            'aspect_ratio': self.aspect_ratio,
            'mood': self.mood,
            'style_name': self.style_name,
            'template_name': self.template_name,
            'negative_prompt': self.negative_prompt,
            'seed': self.seed,
            'provider_name': self.provider_name,
            'provider_kwargs': self.provider_kwargs,
            'output_dir': str(self.output_dir),
            'filename_template': self.filename_template,
            'guidance_scale': self.guidance_scale,
            'num_inference_steps': self.num_inference_steps,
            'enable_safety_checker': self.enable_safety_checker,
            'custom_metadata': self.custom_metadata,
            'action_description': self.action_description,
            'technical': self.technical
        }

        if self.characters:
            base['characters'] = {k: v.to_dict()
                                  for k, v in self.characters.items()}
        if self.environment:
            base['environment'] = self.environment.to_dict()
        if self.cinematography:
            base['cinematography'] = self.cinematography.to_dict()
        if self.lighting:
            base['lighting'] = self.lighting.to_dict()
        if self.style_dna:
            base['style_dna'] = self.style_dna.to_dict()
        if self.continuity:
            base['continuity'] = self.continuity.to_dict()
        if self.persona:
            base['persona'] = self.persona.to_dict()

        return base

    def to_json(self, indent: int = 2) -> str:
        def default_serializer(obj):
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            return str(obj)

        return json.dumps(self.to_dict(), indent=indent, default=default_serializer)


# Predefined personas
DEFAULT_PERSONA = Persona(
    name="Master Filmmaker",
    description=(
        "You are a master filmmaker and cinematographer. You have deep technical knowledge of visual storytelling, "
        "camera technicalities, and emotional pacing. Your goal is to translate abstract concepts into "
        "visually stunning, technically precise video descriptions."
    ),
    expertise=[
        "wide angle shots", "foreground/background depth", "focal point precision",
        "focus pulling", "dynamic camera movement", "lighting theory", "color grading"
    ]
)

# Predefined configurations
DEFAULT_CONFIG = VideoConfig()

CINEMATIC_CONFIG = VideoConfig(
    style_name="cinematic",
    template_name="cinematic",
    mood="dramatic",
    duration_seconds=12,
    aspect_ratio="16:9",
    guidance_scale=8.0,
    num_inference_steps=25
)

QUICK_CONFIG = VideoConfig(
    duration_seconds=4,
    guidance_scale=6.0,
    num_inference_steps=15
)

HIGH_QUALITY_CONFIG = VideoConfig(
    duration_seconds=16,
    guidance_scale=9.0,
    num_inference_steps=30,
    aspect_ratio="16:9"
)
