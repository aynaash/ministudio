"""
Marketing video template for Ministudio.
"""

from ..core import VideoTemplate

marketing_template = VideoTemplate(
    name="marketing",
    description="Marketing and promotional videos",
    duration=8,
    mood="professional",
    style="realistic",
    prompt_template="A compelling scene showing {action}. The orb demonstrates {concept} in a professional marketing style. {style_description}",
    variables={
        "style_description": "with clean, modern aesthetics and professional lighting"
    }
)
