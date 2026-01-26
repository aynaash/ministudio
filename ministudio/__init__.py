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

# Providers (unified system)
from .providers import (
    BaseVideoProvider,
    VertexAIProvider,
    LocalVideoProvider,
    MockVideoProvider,
    create_provider,
    list_providers,
    PROVIDERS
)

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

# New Cinematic Pipeline Components
from .registry import (
    ProviderRegistry,
    RegisteredProvider,
    ProviderMetrics,
    ProviderStatus,
    get_registry,
    set_registry
)

from .scene_graph import (
    SceneGraph,
    Entity,
    EntityType,
    EmotionalState,
    CharacterState,
    CameraState,
    LightingState,
    ConflictRelationship,
    Transform
)

from .shot_plan import (
    ShotPlan,
    Shot,
    Scene,
    CameraSpec,
    LightingSpec,
    CharacterSpec,
    EnvironmentSpec,
    AudioSpec,
    EffectsSpec,
    CharacterDefinition,
    Transition,
    CameraMotion,
    load_shot_plan,
    create_shot_plan
)

from .cinematography import (
    CinematographyProfile,
    CompositionRule,
    LightingStyle,
    StyleEvolution,
    CINEMATOGRAPHY_PROFILES,
    get_profile as get_cinematography_profile,
    create_profile as create_cinematography_profile
)

from .audio_system import (
    AudioTimeline,
    AudioTrack,
    AudioClip,
    AudioTrackType,
    VoiceSettings,
    VoiceStyle,
    MusicCue,
    MusicAction,
    SFXEvent,
    LipSyncData,
    MixSettings,
    AudioGenerator
)

from .prompt_compiler import (
    StructuredPromptCompiler,
    CompiledPrompt,
    PromptPart,
    PromptFormat,
    PromptStyle,
    compile_shot,
    compile_plan,
    quick_prompt
)

from .shot_splitter import (
    ShotSplitter,
    Segment,
    SplitConfig,
    SplitStrategy,
    RetryHandler,
    RetryStrategy,
    split_shot,
    split_plan
)

from .post_processor import (
    PostProcessor,
    ProcessedClip,
    ColorGradeSettings,
    TransitionSpec,
    ProductionManifest,
    COLOR_GRADE_PRESETS,
    get_color_grade,
    export_edl,
    FFmpegCommandBuilder
)

from .production_orchestrator import (
    ProductionOrchestrator,
    ProductionConfig,
    ProductionProgress,
    produce_from_plan,
    quick_produce
)

# Video Text Overlay System
from .text_overlay import (
    TextOverlay,
    TextTrack,
    TextPosition,
    TextAnimation,
    TextOverlayStyle,
    TEXT_STYLES,
    get_text_style,
    Color as TextColor,
    COLORS,
    get_contrasting_color,
    VideoColorAnalyzer,
    SubtitleParser,
    SubtitleEntry,
    LowerThird,
    VideoTextRenderer,
    add_subtitles_to_video,
    add_text_to_video,
    create_subtitle_track
)

# Video Processing Tools
from .video_tools import (
    VideoReader,
    VideoWriter,
    VideoWriterConfig,
    VideoOperations,
    VideoInfo,
    BatchProcessor,
    BatchJob,
    get_video_info,
    trim_video,
    concatenate_videos,
    extract_audio,
    add_audio_to_video
)

# Image Processing Tools
from .image_tools import (
    ImageInfo,
    ImageOperations,
    TextRenderConfig,
    TextRenderer,
    ImageCompositor,
    get_image_info,
    load_image,
    save_image,
    resize_image,
    create_text_image
)

# Transcription System
from .transcription import (
    Transcription,
    Transcriber,
    TranscriptionConfig,
    TranscriptionModel,
    Segment as TranscriptionSegment,
    Word,
    SubtitleGenerator,
    SpeakerDiarizer,
    transcribe,
    transcribe_to_srt,
    transcribe_to_vtt,
    is_transcription_available
)

# Video Text Integration Pipeline
from .video_text import (
    VideoTextPipeline,
    TextPipelineConfig,
    TestVideoManager,
    add_subtitles,
    auto_subtitle,
    add_title,
    add_watermark
)

__version__ = "0.2.1"
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
    
    # Providers
    "BaseVideoProvider",
    "VertexAIProvider",
    "LocalVideoProvider",
    "MockVideoProvider",
    "create_provider",
    "list_providers",
    "PROVIDERS",

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
    "SceneConfig",
    
    # Simple Builder
    "SimpleBuilder",
    "SimpleVideoRequest",
    "generate_video",
    "generate_video_from_description",
    "generate_from_template",
    "interactive_setup",
    "TEMPLATES",
    
    # Audio Agent
    "AudioAgent",
    "AudioTranscriber",
    "PromptCompiler",
    "VideoPrompt",
    "TranscriptionProvider",
    "audio_to_prompt",
    "text_to_prompt",
    "audio_to_video",
    "interactive_audio_session",
    
    # Provider Registry
    "ProviderRegistry",
    "RegisteredProvider",
    "ProviderMetrics",
    "ProviderStatus",
    "get_registry",
    "set_registry",
    
    # Scene Graph
    "SceneGraph",
    "Entity",
    "EntityType",
    "EmotionalState",
    "CharacterState",
    "CameraState",
    "LightingState",
    "ConflictRelationship",
    "Transform",
    
    # Shot Planning
    "ShotPlan",
    "Shot",
    "Scene",
    "CameraSpec",
    "LightingSpec",
    "CharacterSpec",
    "EnvironmentSpec",
    "AudioSpec",
    "EffectsSpec",
    "CharacterDefinition",
    "Transition",
    "CameraMotion",
    "load_shot_plan",
    "create_shot_plan",
    
    # Cinematography
    "CinematographyProfile",
    "CompositionRule",
    "LightingStyle",
    "StyleEvolution",
    "CINEMATOGRAPHY_PROFILES",
    "get_cinematography_profile",
    "create_cinematography_profile",
    
    # Audio System
    "AudioTimeline",
    "AudioTrack",
    "AudioClip",
    "AudioTrackType",
    "VoiceSettings",
    "VoiceStyle",
    "MusicCue",
    "MusicAction",
    "SFXEvent",
    "LipSyncData",
    "MixSettings",
    "AudioGenerator",
    
    # Prompt Compilation
    "StructuredPromptCompiler",
    "CompiledPrompt",
    "PromptPart",
    "PromptFormat",
    "PromptStyle",
    "compile_shot",
    "compile_plan",
    "quick_prompt",
    
    # Shot Splitting
    "ShotSplitter",
    "Segment",
    "SplitConfig",
    "SplitStrategy",
    "RetryHandler",
    "RetryStrategy",
    "split_shot",
    "split_plan",
    
    # Post Processing
    "PostProcessor",
    "ProcessedClip",
    "ColorGradeSettings",
    "TransitionSpec",
    "ProductionManifest",
    "COLOR_GRADE_PRESETS",
    "get_color_grade",
    "export_edl",
    "FFmpegCommandBuilder",
    
    # Production Orchestrator
    "ProductionOrchestrator",
    "ProductionConfig",
    "ProductionProgress",
    "produce_from_plan",
    "quick_produce",
    
    # Text Overlay System
    "TextOverlay",
    "TextTrack",
    "TextPosition",
    "TextAnimation",
    "TextOverlayStyle",
    "TEXT_STYLES",
    "get_text_style",
    "TextColor",
    "COLORS",
    "get_contrasting_color",
    "VideoColorAnalyzer",
    "SubtitleParser",
    "SubtitleEntry",
    "LowerThird",
    "VideoTextRenderer",
    "add_subtitles_to_video",
    "add_text_to_video",
    "create_subtitle_track",
    
    # Video Tools
    "VideoReader",
    "VideoWriter",
    "VideoWriterConfig",
    "VideoOperations",
    "VideoInfo",
    "BatchProcessor",
    "BatchJob",
    "get_video_info",
    "trim_video",
    "concatenate_videos",
    "extract_audio",
    "add_audio_to_video",
    
    # Image Tools
    "ImageInfo",
    "ImageOperations",
    "TextRenderConfig",
    "TextRenderer",
    "ImageCompositor",
    "get_image_info",
    "load_image",
    "save_image",
    "resize_image",
    "create_text_image",
    
    # Transcription
    "Transcription",
    "Transcriber",
    "TranscriptionConfig",
    "TranscriptionModel",
    "TranscriptionSegment",
    "Word",
    "SubtitleGenerator",
    "SpeakerDiarizer",
    "transcribe",
    "transcribe_to_srt",
    "transcribe_to_vtt",
    "is_transcription_available",
    
    # Video Text Pipeline
    "VideoTextPipeline",
    "TextPipelineConfig",
    "TestVideoManager",
    "add_subtitles",
    "auto_subtitle",
    "add_title",
    "add_watermark",
]
