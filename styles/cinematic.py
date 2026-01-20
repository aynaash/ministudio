"""
Cinematic style configuration for Ministudio - Based on AI filmmaking guide.
"""

from ..core import StyleConfig

cinematic_style = StyleConfig(
    name="cinematic",
    description="Professional cinematic style with Hollywood filmmaking techniques",
    characters={
        "protagonist": {
            "appearance": "Dynamically lit character with natural facial expressions",
            "surface": "Photorealistic skin texture with subtle imperfections",
            "glow": "Natural skin highlights and shadows from three-point lighting",
            "motion": "Expressive body language and facial gestures",
            "size": "Life-sized proportions"
        }
    },
    environment={
        "setting": "Professional film set with cinematic lighting setup",
        "lighting": "Three-point lighting system: key light, fill light, back light. Golden hour warmth when appropriate",
        "color_palette": "Cinematic color grading with rich contrasts and natural tones",
        "texture": "Photorealistic materials with depth and detail"
    },
    technical={
        "fps": 24,
        "motion_style": "Smooth, professional camera movements with proper pacing",
        "depth_of_field": "Shallow depth of field for cinematic focus, rule of thirds composition",
        "continuity": "Maintain cinematic consistency with leading lines, camera movement, and lighting continuity",
        "camera_techniques": "Wide establishing shots, medium shots for dialogue, close-ups for emotion, extreme close-ups for tension"
    }
)
