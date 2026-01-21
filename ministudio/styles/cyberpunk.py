"""
Cyberpunk style configuration for Ministudio.
"""

from ..core import StyleConfig

cyberpunk_style = StyleConfig(
    name="cyberpunk",
    description="Neon cyberpunk aesthetic",
    characters={
        "orb": {
            "appearance": "Electric blue orb with pulsing neon circuits",
            "surface": "Glowing digital interfaces and data streams",
            "glow": "Intense electric blue with purple highlights",
            "motion": "Erratic floating with glitch effects",
            "size": "glowing sphere the size of a basketball"
        }
    },
    environment={
        "setting": "Dystopian megacity at night with holographic ads",
        "lighting": "Neon signs, street lights, digital billboards",
        "color_palette": "Electric blues, neon pinks, cyber greens, blacks",
        "texture": "Digital, glitchy, high-tech"
    },
    technical={
        "fps": 30,
        "motion_style": "Jittery, digital movements with occasional glitches",
        "depth_of_field": "Sharp focus with digital artifacts",
        "continuity": "Maintain neon glow and circuit patterns"
    }
)
