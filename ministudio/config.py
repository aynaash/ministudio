"""
Configuration system for Ministudio video generation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
from pathlib import Path
import json
import yaml

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class VideoConfig:
    """Configuration for video generation states and parameters"""

    # Core generation parameters
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    mood: str = "magical"

    # Style and template
    style_name: Optional[str] = "ghibli"
    template_name: Optional[str] = None

    # Prompt customization
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    # Provider settings
    provider_name: str = "mock"
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)

    # Output settings
    output_dir: Union[str, Path] = "./ministudio_output"
    filename_template: str = "{concept}_{timestamp}.mp4"

    # Advanced parameters
    guidance_scale: float = 7.5
    num_inference_steps: int = 20
    enable_safety_checker: bool = True

    # Custom parameters
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoConfig':
        """Create config from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'VideoConfig':
        """Create config from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'VideoConfig':
        """Create config from YAML string"""
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML support")
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'VideoConfig':
        """Load config from file (JSON or YAML)"""
        path = Path(file_path)
        if path.suffix.lower() in ['.yaml', '.yml']:
            with open(path, 'r') as f:
                return cls.from_yaml(f.read())
        else:
            with open(path, 'r') as f:
                return cls.from_json(f.read())

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'duration_seconds': self.duration_seconds,
            'aspect_ratio': self.aspect_ratio,
            'mood': self.mood,
            'style_name': self.style_name,
            'template_name': self.template_name,
            'negative_prompt': self.negative_prompt,
            'seed': self.seed,
            'provider_name': self.provider_name,
            'provider_kwargs': self.provider_kwargs,
            'output_dir': str(self.output_dir),
            'filename_template': self.filename_template,
            'guidance_scale': self.guidance_scale,
            'num_inference_steps': self.num_inference_steps,
            'enable_safety_checker': self.enable_safety_checker,
            'custom_metadata': self.custom_metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert config to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: Union[str, Path], format: str = 'json') -> None:
        """Save config to file"""
        path = Path(file_path)
        if format.lower() == 'yaml':
            if not HAS_YAML:
                raise ImportError("PyYAML is required for YAML support")
            with open(path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        else:
            with open(path, 'w') as f:
                f.write(self.to_json())

    def merge(self, other: 'VideoConfig') -> 'VideoConfig':
        """Merge with another config (other takes precedence)"""
        current_dict = self.to_dict()
        other_dict = other.to_dict()
        merged = {**current_dict, **other_dict}
        return VideoConfig.from_dict(merged)

    def validate(self) -> None:
        """Validate configuration parameters"""
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if self.aspect_ratio not in ["16:9", "1:1", "9:16", "4:3", "3:4"]:
            raise ValueError("Invalid aspect_ratio")
        if self.guidance_scale <= 0:
            raise ValueError("guidance_scale must be positive")
        if self.num_inference_steps <= 0:
            raise ValueError("num_inference_steps must be positive")


# Predefined configurations for common use cases
DEFAULT_CONFIG = VideoConfig()

CINEMATIC_CONFIG = VideoConfig(
    style_name="cinematic",
    template_name="cinematic",
    mood="dramatic",
    duration_seconds=12,
    aspect_ratio="16:9",
    guidance_scale=8.0,
    num_inference_steps=25
)

QUICK_CONFIG = VideoConfig(
    duration_seconds=4,
    guidance_scale=6.0,
    num_inference_steps=15
)

HIGH_QUALITY_CONFIG = VideoConfig(
    duration_seconds=16,
    guidance_scale=9.0,
    num_inference_steps=30,
    aspect_ratio="16:9"
)
