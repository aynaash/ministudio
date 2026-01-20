"""
Ghibli style configuration for Ministudio.
"""

from ..core import StyleConfig

ghibli_style = StyleConfig(
    name="ghibli",
    description="Studio Ghibli aesthetic",
    characters={
        "orb": {
            "appearance": "Golden glowing orb with warm inner light",
            "surface": "Translucent with gentle data-circuit patterns flowing inside",
            "glow": "Soft golden with ethereal teal accents",
            "motion": "Slow floating drift, gentle bobbing",
            "size": "tennis ball sized"
        }
    },
    environment={
        "setting": "Cozy study room suspended in twilight sky",
        "lighting": "Cinematic golden hour, volumetric light rays",
        "color_palette": "Warm golds, deep teals, soft whites",
        "texture": "Painterly, hand-drawn feel"
    },
    technical={
        "fps": 24,
        "motion_style": "Hand-animated organic feel",
        "depth_of_field": "Shallow, cinematic",
        "continuity": "Maintain character appearance across frames"
    }
)
