"""
Cinematography Module
=====================
Professional cinematography tools and prompt enhancement.

Features:
- Shot composition rules
- Camera movement patterns
- Lighting recipes
- Visual style guides
- Prompt enhancement with cinematography terms
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CompositionRule(Enum):
    """Classic composition rules."""
    RULE_OF_THIRDS = "rule_of_thirds"
    GOLDEN_RATIO = "golden_ratio"
    CENTER = "center"
    LEADING_SPACE = "leading_space"
    SYMMETRY = "symmetry"
    DUTCH_ANGLE = "dutch_angle"
    FRAME_WITHIN_FRAME = "frame_within_frame"
    DIAGONAL = "diagonal"
    TRIANGULAR = "triangular"


class LightingStyle(Enum):
    """Classic lighting styles."""
    HIGH_KEY = "high_key"  # Bright, low contrast
    LOW_KEY = "low_key"  # Dark, high contrast
    REMBRANDT = "rembrandt"  # Classic portrait lighting
    SPLIT = "split"  # Half face lit
    BUTTERFLY = "butterfly"  # Above, creates shadow under nose
    LOOP = "loop"  # Small shadow from nose
    NATURAL = "natural"  # Window/sun light
    SILHOUETTE = "silhouette"  # Backlit, subject dark
    CHIAROSCURO = "chiaroscuro"  # Strong contrast
    NOIR = "noir"  # Hard shadows, moody


@dataclass
class CinematographyProfile:
    """Complete cinematography profile for a shot."""
    
    # Shot composition
    shot_type: str = "medium"
    composition: CompositionRule = CompositionRule.RULE_OF_THIRDS
    depth_layers: List[str] = field(default_factory=lambda: ["foreground", "midground", "background"])
    
    # Camera
    lens: str = "35mm"
    focal_length: int = 35
    aperture: str = "f/2.8"
    depth_of_field: str = "medium"  # shallow, medium, deep
    motion: str = "static"
    motion_speed: float = 1.0
    
    # Framing
    headroom: str = "standard"  # tight, standard, loose
    look_room: str = "standard"  # tight, standard, generous
    horizon_line: str = "thirds"  # bottom_third, middle, top_third
    
    # Lighting
    lighting_style: LightingStyle = LightingStyle.NATURAL
    light_direction: str = "front_left"
    contrast_ratio: str = "4:1"  # Fill to key ratio
    color_temperature: int = 5600  # Kelvin
    
    # Atmosphere
    atmosphere: str = "clear"  # clear, hazy, foggy, smoky
    time_of_day: str = "day"
    weather: str = "clear"
    
    # Color grading
    color_grade: str = "neutral"  # neutral, warm, cool, teal_orange, etc.
    saturation: str = "normal"  # muted, normal, vibrant
    contrast: str = "normal"  # low, normal, high
    
    def to_prompt_parts(self) -> List[str]:
        """Generate prompt enhancement parts from cinematography settings."""
        parts = []
        
        # Shot type description
        shot_type_desc = {
            "extreme_wide": "extreme wide shot showing vast landscape",
            "wide": "wide establishing shot",
            "full": "full body shot",
            "medium_wide": "medium wide shot from knees up",
            "medium": "medium shot from waist up",
            "medium_close": "medium close-up from chest up",
            "close_up": "close-up shot focusing on face",
            "extreme_close_up": "extreme close-up on details",
            "insert": "insert shot of detail",
            "pov": "point of view shot",
            "over_shoulder": "over-the-shoulder shot",
            "two_shot": "two-shot framing both characters"
        }
        if self.shot_type in shot_type_desc:
            parts.append(shot_type_desc[self.shot_type])
        
        # Lens characteristics
        lens_desc = {
            "14mm": "ultra-wide 14mm lens, dramatic perspective distortion",
            "24mm": "wide 24mm lens, environmental context",
            "35mm": "35mm lens, natural perspective",
            "50mm": "50mm lens, cinematic standard",
            "85mm": "85mm portrait lens, flattering compression",
            "135mm": "telephoto 135mm lens, compressed perspective",
            "200mm": "long telephoto lens, extreme compression"
        }
        if self.lens in lens_desc:
            parts.append(f"shot with {lens_desc[self.lens]}")
        
        # Aperture/DOF
        dof_desc = {
            "shallow": "shallow depth of field with bokeh background blur",
            "medium": "moderate depth of field",
            "deep": "deep focus with sharp foreground to background"
        }
        if self.depth_of_field in dof_desc:
            parts.append(dof_desc[self.depth_of_field])
        
        # Composition
        comp_desc = {
            CompositionRule.RULE_OF_THIRDS: "composed with rule of thirds",
            CompositionRule.GOLDEN_RATIO: "golden ratio composition",
            CompositionRule.CENTER: "centered symmetrical composition",
            CompositionRule.LEADING_SPACE: "generous leading space for movement",
            CompositionRule.SYMMETRY: "perfect bilateral symmetry",
            CompositionRule.DUTCH_ANGLE: "dramatic Dutch angle tilt",
            CompositionRule.FRAME_WITHIN_FRAME: "frame-within-frame composition",
            CompositionRule.DIAGONAL: "dynamic diagonal composition",
            CompositionRule.TRIANGULAR: "stable triangular composition"
        }
        if self.composition in comp_desc:
            parts.append(comp_desc[self.composition])
        
        # Lighting style
        light_desc = {
            LightingStyle.HIGH_KEY: "bright high-key lighting, minimal shadows",
            LightingStyle.LOW_KEY: "moody low-key lighting, deep shadows",
            LightingStyle.REMBRANDT: "classic Rembrandt lighting with triangle highlight",
            LightingStyle.SPLIT: "dramatic split lighting, half face in shadow",
            LightingStyle.BUTTERFLY: "glamorous butterfly lighting from above",
            LightingStyle.SILHOUETTE: "backlit silhouette, subject in shadow",
            LightingStyle.CHIAROSCURO: "chiaroscuro lighting with strong contrast",
            LightingStyle.NOIR: "film noir lighting with hard shadows"
        }
        if self.lighting_style in light_desc:
            parts.append(light_desc[self.lighting_style])
        
        # Color temperature
        temp_desc = {
            3200: "warm tungsten lighting",
            4500: "neutral mixed lighting",
            5600: "daylight balanced",
            6500: "cool overcast lighting",
            8000: "blue hour cold light"
        }
        closest_temp = min(temp_desc.keys(), key=lambda x: abs(x - self.color_temperature))
        parts.append(temp_desc[closest_temp])
        
        # Atmosphere
        if self.atmosphere != "clear":
            atmo_desc = {
                "hazy": "atmospheric haze in the air",
                "foggy": "fog creating depth and mystery",
                "smoky": "smoke particles catching the light",
                "dusty": "dust particles visible in light beams"
            }
            if self.atmosphere in atmo_desc:
                parts.append(atmo_desc[self.atmosphere])
        
        # Time of day
        time_desc = {
            "dawn": "dawn light, soft pink and blue hues",
            "morning": "morning light, warm and gentle",
            "day": "midday sunlight",
            "afternoon": "afternoon light with long shadows",
            "golden_hour": "golden hour magic light, warm orange glow",
            "dusk": "dusk light, purple and blue tones",
            "blue_hour": "blue hour, soft ambient light",
            "night": "night scene, artificial lighting"
        }
        if self.time_of_day in time_desc:
            parts.append(time_desc[self.time_of_day])
        
        # Color grading
        grade_desc = {
            "neutral": "",
            "warm": "warm color grading, orange tones",
            "cool": "cool color grading, blue tones",
            "teal_orange": "teal and orange color grading",
            "vintage": "vintage film color grading",
            "desaturated": "desaturated muted colors",
            "high_contrast": "high contrast look",
            "cinematic": "cinematic color grading"
        }
        if self.color_grade in grade_desc and grade_desc[self.color_grade]:
            parts.append(grade_desc[self.color_grade])
        
        # Camera motion
        if self.motion != "static":
            motion_desc = {
                "pan_left": "smooth pan left",
                "pan_right": "smooth pan right",
                "tilt_up": "tilt up revealing",
                "tilt_down": "tilt down descending",
                "dolly_in": "dolly in moving closer",
                "dolly_out": "dolly out pulling away",
                "crane_up": "crane shot rising",
                "crane_down": "crane shot descending",
                "tracking": "tracking shot following movement",
                "steadicam": "smooth steadicam movement",
                "handheld": "handheld documentary feel"
            }
            if self.motion in motion_desc:
                parts.append(motion_desc[self.motion])
        
        return parts
    
    def enhance_prompt(self, base_prompt: str) -> str:
        """Enhance a base prompt with cinematography details."""
        parts = self.to_prompt_parts()
        if parts:
            enhancement = ", ".join(parts)
            return f"{base_prompt}, {enhancement}"
        return base_prompt


# ============ Pre-built Cinematography Profiles ============

CINEMATOGRAPHY_PROFILES: Dict[str, CinematographyProfile] = {
    "establishing_wide": CinematographyProfile(
        shot_type="wide",
        lens="24mm",
        focal_length=24,
        depth_of_field="deep",
        composition=CompositionRule.RULE_OF_THIRDS,
        lighting_style=LightingStyle.NATURAL,
        motion="static"
    ),
    
    "dramatic_close_up": CinematographyProfile(
        shot_type="close_up",
        lens="85mm",
        focal_length=85,
        aperture="f/1.8",
        depth_of_field="shallow",
        composition=CompositionRule.RULE_OF_THIRDS,
        lighting_style=LightingStyle.REMBRANDT,
        motion="static"
    ),
    
    "action_tracking": CinematographyProfile(
        shot_type="medium",
        lens="35mm",
        focal_length=35,
        depth_of_field="medium",
        composition=CompositionRule.LEADING_SPACE,
        lighting_style=LightingStyle.NATURAL,
        motion="tracking",
        motion_speed=1.0
    ),
    
    "intimate_dialogue": CinematographyProfile(
        shot_type="medium_close",
        lens="50mm",
        focal_length=50,
        aperture="f/2.0",
        depth_of_field="shallow",
        composition=CompositionRule.RULE_OF_THIRDS,
        lighting_style=LightingStyle.LOOP,
        motion="static"
    ),
    
    "noir_mystery": CinematographyProfile(
        shot_type="medium",
        lens="35mm",
        focal_length=35,
        depth_of_field="medium",
        composition=CompositionRule.DIAGONAL,
        lighting_style=LightingStyle.NOIR,
        contrast_ratio="8:1",
        color_grade="desaturated",
        atmosphere="smoky"
    ),
    
    "epic_landscape": CinematographyProfile(
        shot_type="extreme_wide",
        lens="14mm",
        focal_length=14,
        depth_of_field="deep",
        composition=CompositionRule.GOLDEN_RATIO,
        horizon_line="bottom_third",
        lighting_style=LightingStyle.NATURAL,
        time_of_day="golden_hour",
        color_grade="cinematic"
    ),
    
    "documentary_handheld": CinematographyProfile(
        shot_type="medium",
        lens="35mm",
        focal_length=35,
        depth_of_field="deep",
        composition=CompositionRule.CENTER,
        lighting_style=LightingStyle.NATURAL,
        motion="handheld",
        color_grade="neutral",
        saturation="normal"
    ),
    
    "romantic_soft": CinematographyProfile(
        shot_type="medium_close",
        lens="85mm",
        focal_length=85,
        aperture="f/1.4",
        depth_of_field="shallow",
        composition=CompositionRule.RULE_OF_THIRDS,
        lighting_style=LightingStyle.BUTTERFLY,
        color_temperature=4500,
        color_grade="warm",
        atmosphere="hazy"
    ),
    
    "horror_tension": CinematographyProfile(
        shot_type="close_up",
        lens="24mm",
        focal_length=24,
        depth_of_field="deep",
        composition=CompositionRule.DUTCH_ANGLE,
        lighting_style=LightingStyle.LOW_KEY,
        contrast_ratio="10:1",
        color_grade="desaturated",
        color_temperature=6500,
        atmosphere="foggy"
    ),
    
    "product_hero": CinematographyProfile(
        shot_type="close_up",
        lens="50mm",
        focal_length=50,
        aperture="f/4",
        depth_of_field="medium",
        composition=CompositionRule.CENTER,
        lighting_style=LightingStyle.HIGH_KEY,
        color_grade="neutral",
        contrast="normal"
    )
}


def get_profile(name: str) -> CinematographyProfile:
    """Get a pre-built cinematography profile."""
    if name in CINEMATOGRAPHY_PROFILES:
        return CINEMATOGRAPHY_PROFILES[name]
    return CinematographyProfile()


def create_profile(**kwargs) -> CinematographyProfile:
    """Create a custom cinematography profile."""
    return CinematographyProfile(**kwargs)


# ============ Shot Progression Patterns ============

@dataclass
class ShotProgression:
    """A sequence of cinematography profiles for a scene."""
    name: str
    profiles: List[CinematographyProfile]
    descriptions: List[str]
    
    def __iter__(self):
        return iter(zip(self.profiles, self.descriptions))
    
    def __len__(self):
        return len(self.profiles)


def create_establishing_sequence() -> ShotProgression:
    """Create standard establishing shot sequence."""
    return ShotProgression(
        name="establishing",
        profiles=[
            CinematographyProfile(
                shot_type="extreme_wide",
                lens="14mm",
                depth_of_field="deep",
                motion="static"
            ),
            CinematographyProfile(
                shot_type="wide",
                lens="24mm",
                depth_of_field="deep",
                motion="dolly_in"
            ),
            CinematographyProfile(
                shot_type="medium",
                lens="35mm",
                depth_of_field="medium",
                motion="static"
            )
        ],
        descriptions=[
            "Extreme wide establishing the location",
            "Wide shot introducing the scene",
            "Medium shot on the subject"
        ]
    )


def create_tension_building_sequence() -> ShotProgression:
    """Create tension-building shot sequence."""
    return ShotProgression(
        name="tension",
        profiles=[
            CinematographyProfile(
                shot_type="medium",
                lens="35mm",
                motion="static",
                lighting_style=LightingStyle.LOW_KEY
            ),
            CinematographyProfile(
                shot_type="close_up",
                lens="50mm",
                depth_of_field="shallow",
                motion="dolly_in",
                lighting_style=LightingStyle.SPLIT
            ),
            CinematographyProfile(
                shot_type="extreme_close_up",
                lens="85mm",
                depth_of_field="shallow",
                motion="static",
                lighting_style=LightingStyle.LOW_KEY
            )
        ],
        descriptions=[
            "Medium shot observing",
            "Close-up building intensity",
            "Extreme close-up on reaction"
        ]
    )


def create_revelation_sequence() -> ShotProgression:
    """Create revelation/discovery shot sequence."""
    return ShotProgression(
        name="revelation",
        profiles=[
            CinematographyProfile(
                shot_type="medium",
                lens="50mm",
                motion="dolly_in"
            ),
            CinematographyProfile(
                shot_type="close_up",
                lens="85mm",
                depth_of_field="shallow",
                motion="static"
            ),
            CinematographyProfile(
                shot_type="pov",
                lens="35mm",
                motion="pan_right"
            ),
            CinematographyProfile(
                shot_type="close_up",
                lens="50mm",
                depth_of_field="shallow",
                motion="static",
                lighting_style=LightingStyle.REMBRANDT
            )
        ],
        descriptions=[
            "Approach the subject",
            "Reaction shot before revelation",
            "POV of what they see",
            "Close-up on reaction to revelation"
        ]
    )


# ============ Depth Layer Descriptions ============

def generate_depth_layers(
    foreground: Optional[str] = None,
    midground: Optional[str] = None,
    background: Optional[str] = None
) -> str:
    """Generate depth layer description for prompts."""
    parts = []
    if foreground:
        parts.append(f"foreground: {foreground}")
    if midground:
        parts.append(f"midground: {midground}")
    if background:
        parts.append(f"background: {background}")
    
    if parts:
        return f"[{', '.join(parts)}]"
    return ""


# ============ Aspect Ratio Composition Guides ============

ASPECT_RATIO_GUIDES = {
    "16:9": {
        "rule_of_thirds": {
            "power_points": [(0.33, 0.33), (0.66, 0.33), (0.33, 0.66), (0.66, 0.66)],
            "horizontal_lines": [0.33, 0.66],
            "vertical_lines": [0.33, 0.66],
            "description": "Standard widescreen, ideal for cinematic content"
        }
    },
    "2.39:1": {
        "rule_of_thirds": {
            "power_points": [(0.33, 0.33), (0.66, 0.33), (0.33, 0.66), (0.66, 0.66)],
            "horizontal_lines": [0.33, 0.66],
            "vertical_lines": [0.33, 0.66],
            "description": "Anamorphic widescreen, epic cinematic feel"
        }
    },
    "1:1": {
        "rule_of_thirds": {
            "power_points": [(0.33, 0.33), (0.66, 0.33), (0.33, 0.66), (0.66, 0.66)],
            "description": "Square format, ideal for social media"
        }
    },
    "9:16": {
        "rule_of_thirds": {
            "power_points": [(0.33, 0.33), (0.66, 0.33), (0.33, 0.66), (0.66, 0.66)],
            "description": "Vertical format for mobile/TikTok content"
        }
    }
}


def get_composition_guide(
    aspect_ratio: str = "16:9",
    rule: CompositionRule = CompositionRule.RULE_OF_THIRDS
) -> Dict[str, Any]:
    """Get composition guide for aspect ratio and rule."""
    if aspect_ratio in ASPECT_RATIO_GUIDES:
        guides = ASPECT_RATIO_GUIDES[aspect_ratio]
        rule_name = rule.value
        if rule_name in guides:
            return guides[rule_name]
    return {}


# ============ Style Evolution ============

@dataclass
class StyleEvolution:
    """Track how visual style evolves through a sequence."""
    
    # Lighting progression
    lighting_intensity_start: float = 1.0
    lighting_intensity_end: float = 1.0
    color_temp_start: int = 5600
    color_temp_end: int = 5600
    
    # Color progression
    saturation_start: float = 1.0
    saturation_end: float = 1.0
    contrast_start: float = 1.0
    contrast_end: float = 1.0
    
    # Atmosphere
    atmosphere_density_start: float = 0.0
    atmosphere_density_end: float = 0.0
    
    def get_values_at(self, progress: float) -> Dict[str, float]:
        """Get interpolated values at a progress point (0.0 to 1.0)."""
        def lerp(start, end, t):
            return start + (end - start) * t
        
        return {
            "lighting_intensity": lerp(self.lighting_intensity_start, self.lighting_intensity_end, progress),
            "color_temperature": lerp(self.color_temp_start, self.color_temp_end, progress),
            "saturation": lerp(self.saturation_start, self.saturation_end, progress),
            "contrast": lerp(self.contrast_start, self.contrast_end, progress),
            "atmosphere_density": lerp(self.atmosphere_density_start, self.atmosphere_density_end, progress)
        }


# Pre-built evolutions
STYLE_EVOLUTIONS = {
    "dawn_to_day": StyleEvolution(
        color_temp_start=3200,
        color_temp_end=5600,
        lighting_intensity_start=0.5,
        lighting_intensity_end=1.0,
        atmosphere_density_start=0.3,
        atmosphere_density_end=0.0
    ),
    "day_to_dusk": StyleEvolution(
        color_temp_start=5600,
        color_temp_end=3500,
        lighting_intensity_start=1.0,
        lighting_intensity_end=0.6,
        saturation_start=1.0,
        saturation_end=1.2
    ),
    "tension_build": StyleEvolution(
        lighting_intensity_start=1.0,
        lighting_intensity_end=0.5,
        contrast_start=1.0,
        contrast_end=1.4,
        saturation_start=1.0,
        saturation_end=0.7
    ),
    "revelation": StyleEvolution(
        lighting_intensity_start=0.5,
        lighting_intensity_end=1.2,
        contrast_start=1.2,
        contrast_end=0.9,
        saturation_start=0.7,
        saturation_end=1.1
    )
}


def get_style_evolution(name: str) -> StyleEvolution:
    """Get a pre-built style evolution."""
    return STYLE_EVOLUTIONS.get(name, StyleEvolution())
