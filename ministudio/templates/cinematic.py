"""
Cinematic filmmaking template for Ministudio - Based on AI filmmaking guide.
"""

from ..core import VideoTemplate

cinematic_template = VideoTemplate(
    name="cinematic",
    description="Professional cinematic scene with Hollywood filmmaking techniques and shot progression",
    duration=12,
    mood="dramatic",
    style="cinematic",
    prompt_template="Create a cinematic film scene showing {action} in a professional Hollywood style. Use proper shot progression: start with a WIDE ESTABLISHING SHOT to set the scene, transition to MEDIUM SHOT for context, move to CLOSE-UP for emotional connection, build tension with EXTREME CLOSE-UP, then return to MEDIUM SHOT. Follow cinematic rules: rule of thirds composition, leading lines, shallow depth of field, three-point lighting with golden hour warmth. Camera movements include smooth pans and tilts. The concept is: {concept}. Maintain photorealistic quality with natural lighting and textures.",
    variables={
        "style_description": "in a cinematic Hollywood style with professional filmmaking techniques, proper shot progression, and dramatic lighting"
    }
)
