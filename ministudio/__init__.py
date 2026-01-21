"""
Ministudio - Model-Agnostic AI Video Generation Framework
=========================================================

The Model-Agnostic AI Video Framework - Make AI video generation
as consistent as CSS makes web styling.
"""

# Core Interfaces
from .interfaces import (
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoProvider
)

# Core Logic
from .core import (
    Ministudio,
    StyleConfig,
    VideoTemplate
)

# Configuration & Data Structures
from .config import (
    VideoConfig,
    DEFAULT_CONFIG,
    CINEMATIC_CONFIG,
    QUICK_CONFIG,
    HIGH_QUALITY_CONFIG,
    Character,
    Environment,
    Cinematography,
    LightingDirector,
    StyleDNA,
    ContinuityEngine,
    Camera,
    LightSource,
    Color,
    Vector3
)

# State & Orchestration
from .state import VideoStateMachine, WorldState
from .orchestrator import VideoOrchestrator

__version__ = "0.1.0"
__author__ = "Ministudio Team"
__email__ = "team@ministudio.ai"

__all__ = [
    # Core Classes
    "Ministudio",
    "VideoOrchestrator",
    "VideoStateMachine",
    "VideoTemplate",
    "StyleConfig",

    # Interfaces
    "VideoGenerationRequest",
    "VideoGenerationResult",
    "VideoProvider",

    # Config & Data
    "VideoConfig",
    "DEFAULT_CONFIG",
    "CINEMATIC_CONFIG",
    "QUICK_CONFIG",
    "HIGH_QUALITY_CONFIG",

    # Programmable Elements
    "Character",
    "Environment",
    "Cinematography",
    "LightingDirector",
    "StyleDNA",
    "ContinuityEngine",
    "Camera",
    "LightSource",
    "Color",
    "Vector3"
]
