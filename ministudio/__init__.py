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
    DEFAULT_PERSONA,
    Persona,
    Character,
    Environment,
    Cinematography,
    LightingDirector,
    StyleDNA,
    ContinuityEngine,
    Camera,
    LightSource,
    Color,
    Vector3,
    ShotType,
    ShotConfig,
    SceneConfig
)

# State & Orchestration
from .state import VideoStateMachine, WorldState
from .orchestrator import VideoOrchestrator

# Simple Builder (Non-Technical Interface)
from .simple_builder import (
    SimpleBuilder,
    SimpleVideoRequest,
    generate_video,
    generate_video_from_description,
    generate_from_template,
    interactive_setup,
    TEMPLATES
)

# Audio Agent (Voice-to-Video)
from .audio_agent import (
    AudioAgent,
    AudioTranscriber,
    PromptCompiler,
    VideoPrompt,
    TranscriptionProvider,
    audio_to_prompt,
    text_to_prompt,
    audio_to_video,
    interactive_audio_session
)

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
    "Persona",
    "DEFAULT_PERSONA",
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
    "Vector3",
    "ShotType",
    "ShotConfig",
    "SceneConfig"
]
