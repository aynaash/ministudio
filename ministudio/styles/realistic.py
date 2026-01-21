"""
Realistic style configuration for Ministudio.
"""

from ..core import StyleConfig

realistic_style = StyleConfig(
    name="realistic",
    description="Photorealistic aesthetic",
    characters={
        "orb": {
            "appearance": "Polished metallic sphere with realistic reflections",
            "surface": "Smooth chrome surface with environmental reflections",
            "glow": "Subtle internal illumination with realistic light scattering",
            "motion": "Smooth, physics-based floating with inertia",
            "size": "perfect sphere approximately 6 inches in diameter"
        }
    },
    environment={
        "setting": "Modern laboratory or clean room environment",
        "lighting": "Professional studio lighting with soft shadows",
        "color_palette": "Natural colors, metallic silvers, clean whites",
        "texture": "Photorealistic materials and surfaces"
    },
    technical={
        "fps": 30,
        "motion_style": "Realistic physics-based movement",
        "depth_of_field": "Natural depth of field with focus blur",
        "continuity": "Maintain realistic lighting and reflections"
    }
)
