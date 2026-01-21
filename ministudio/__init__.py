"""
Ministudio - Model-Agnostic AI Video Generation Framework
=========================================================

The Model-Agnostic AI Video Framework - Make AI video generation
as consistent as CSS makes web styling.
"""

from .core import (
    Ministudio,
    StyleConfig,
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoProvider,
    PromptEngine,
    VideoTemplate
)
from .config import VideoConfig, DEFAULT_CONFIG, CINEMATIC_CONFIG, QUICK_CONFIG, HIGH_QUALITY_CONFIG

__version__ = "0.1.0"
__author__ = "Ministudio Team"
__email__ = "team@ministudio.ai"

__all__ = [
    "Ministudio",
    "StyleConfig",
    "VideoGenerationRequest",
    "VideoGenerationResult",
    "VideoProvider",
    "PromptEngine",
    "VideoTemplate",
    "VideoConfig",
    "DEFAULT_CONFIG",
    "CINEMATIC_CONFIG",
    "QUICK_CONFIG",
    "HIGH_QUALITY_CONFIG"
]
