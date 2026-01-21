"""
Explainer video template for Ministudio.
"""

from ..core import VideoTemplate

explainer_template = VideoTemplate(
    name="explainer",
    description="Educational explainer videos",
    duration=10,
    mood="educational",
    style="ghibli",
    prompt_template="A scene showing {action}. The orb explains {concept} in an educational way. {style_description}",
    variables={
        "style_description": "in a Studio Ghibli style with warm lighting and gentle animations"
    }
)
