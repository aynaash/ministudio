"""
CineLang Demo Runner
====================
Execute the 3-minute meta-demo using multiple AI video providers.

This script:
1. Loads the CineLang JSON specification
2. Generates video clips using Veo and HuggingFace models
3. Assembles the final demo video

Usage:
    python -m examples.demo_runner
    
    # Or with specific provider
    python -m examples.demo_runner --provider huggingface
    python -m examples.demo_runner --provider veo
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ministudio import (
    # Shot planning
    ShotPlan, Shot, Scene,
    load_shot_plan, create_shot_plan,
    
    # Prompt compilation
    StructuredPromptCompiler, compile_shot,
    
    # Video tools
    VideoOperations, get_video_info,
    
    # Text overlay
    VideoTextPipeline, TextOverlay, TextPosition, TextTrack,
    
    # Registry
    ProviderRegistry, get_registry,
)

from ministudio.providers.veo import VeoProvider, VeoConfig, VeoGenerationResult
from ministudio.providers.huggingface import (
    HuggingFaceProvider, HFVideoConfig, HFVideoModel, HFGenerationResult
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ Demo Configuration ============

DEMO_CONFIG = {
    "meta": {
        "title": "CineLang Meta-Demo",
        "duration_sec": 180,
        "aspect_ratio": "16:9",
        "fps": 24
    },
    "style": {
        "look": "painterly cinematic",
        "lighting": "warm desk lamp + cool monitor glow",
        "color_grade": "cold-to-warm gradient",
        "lens_flare": True,
        "depth_of_field": "shallow"
    },
    "characters": {
        "you": {
            "ref": "assets/you_portrait.png",
            "description": "Developer at desk, focused, typing, wearing casual attire",
            "continuity_lock": True
        }
    },
    "environments": {
        "coding_desk": {
            "description": "Cluttered laptop desk, coding environment, keyboard, lamp, warm overhead lighting",
            "mood": "focused, creative",
            "lighting": "warm overhead lamp + cool laptop glow"
        },
        "ai_scene_screen": {
            "description": "Laptop display showing AI-generated cinematic scene",
            "mood": "magical, painterly, Ghibli-style"
        }
    }
}

# Shot definitions for the demo
DEMO_SHOTS = [
    {
        "id": "shot_1_intro",
        "scene": "scene_1_intro",
        "type": "wide",
        "lens": "35mm",
        "movement": "slow_dolly_push",
        "duration_sec": 20,
        "prompt": "Cinematic wide shot of a developer's desk workspace, warm lamp light, laptop glowing softly, keyboard visible, minimalist aesthetic, shallow depth of field, evening lighting, painterly style",
        "negative_prompt": "blurry, low quality, distorted, cartoon"
    },
    {
        "id": "shot_2_typing",
        "scene": "scene_1_intro",
        "type": "medium",
        "lens": "50mm",
        "movement": "over_the_shoulder",
        "duration_sec": 15,
        "prompt": "Over-the-shoulder medium shot of hands typing on laptop keyboard, code visible on screen, warm lamp glow, focused developer, cinematic lighting, film grain",
        "negative_prompt": "blurry, distorted, low quality"
    },
    {
        "id": "shot_3_screen",
        "scene": "scene_2_tool",
        "type": "closeup",
        "lens": "50mm",
        "movement": "push_in",
        "duration_sec": 20,
        "prompt": "Close-up of laptop screen showing terminal with code compilation, glowing interface, cool blue light on face, cinematic push-in camera movement, dramatic lighting",
        "negative_prompt": "blurry, pixelated"
    },
    {
        "id": "shot_4_reaction",
        "scene": "scene_2_tool",
        "type": "medium",
        "lens": "35mm",
        "movement": "handheld_subtle",
        "duration_sec": 10,
        "prompt": "Medium shot of developer leaning back, slight smile of anticipation, laptop glow illuminating face, warm and cool lighting mix, cinematic film style",
        "negative_prompt": "cartoon, anime, blurry"
    },
    {
        "id": "shot_5_ai_scene",
        "scene": "scene_3_ai_insert",
        "type": "screen_insert",
        "duration_sec": 15,
        "prompt": "Painterly Ghibli-style animated scene, soft magical forest with gentle light rays, a lone figure walking on a path, dreamy atmosphere, watercolor aesthetic, smooth gentle motion",
        "negative_prompt": "realistic, harsh lighting, dark"
    },
    {
        "id": "shot_6_wonder",
        "scene": "scene_3_ai_insert",
        "type": "wide",
        "lens": "35mm",
        "movement": "slow_push_in",
        "duration_sec": 20,
        "prompt": "Wide shot of developer watching laptop with wonder, Ghibli animation playing on screen casting magical glow, cinematic composition, warm and cool lighting contrast, shallow DOF",
        "negative_prompt": "dark, gloomy, cartoon"
    },
    {
        "id": "shot_7_meta",
        "scene": "scene_4_meta_demo",
        "type": "medium",
        "lens": "50mm",
        "movement": "static",
        "duration_sec": 30,
        "prompt": "Medium shot from side angle showing laptop screen with animated content and JSON code overlay, developer visible, professional cinematic lighting, tech demo aesthetic",
        "negative_prompt": "blurry, unprofessional"
    },
    {
        "id": "shot_8_satisfaction",
        "scene": "scene_4_meta_demo",
        "type": "closeup",
        "lens": "85mm",
        "movement": "slow_push_in",
        "duration_sec": 20,
        "prompt": "Intimate close-up portrait of developer with satisfied smile, laptop glow bathing face in soft light, shallow depth of field, cinematic film grain, warm tones",
        "negative_prompt": "unflattering, harsh shadows"
    },
    {
        "id": "shot_9_closure",
        "scene": "scene_5_closure",
        "type": "wide",
        "lens": "35mm",
        "movement": "pull_back_dolly",
        "duration_sec": 30,
        "prompt": "Cinematic wide pullback shot revealing full desk setup, laptop glowing with animated content, evening atmosphere, lens flare from lamp, gradual fade to warm tones, closure feeling",
        "negative_prompt": "harsh, abrupt, cluttered"
    }
]


@dataclass
class DemoGenerationResult:
    """Result from demo generation."""
    
    shot_id: str
    provider: str
    success: bool
    video_path: Optional[str] = None
    duration: float = 0.0
    prompt: str = ""
    generation_time: float = 0.0
    error: Optional[str] = None


@dataclass
class DemoRunnerConfig:
    """Configuration for demo runner."""
    
    output_dir: str = "output/demo"
    providers: List[str] = field(default_factory=lambda: ["huggingface"])
    
    # Provider-specific settings
    veo_project_id: Optional[str] = None
    hf_model: str = "cerspense/zeroscope_v2_576w"
    
    # Generation settings
    generate_all_shots: bool = True
    shot_ids: Optional[List[str]] = None  # Specific shots to generate
    
    # Assembly settings
    add_titles: bool = True
    add_transitions: bool = True
    
    # Output
    final_video_path: str = "output/demo/cinelang_demo.mp4"


class DemoRunner:
    """
    Execute the CineLang demo using multiple providers.
    """
    
    def __init__(self, config: Optional[DemoRunnerConfig] = None):
        self.config = config or DemoRunnerConfig()
        self.providers: Dict[str, Any] = {}
        self.results: List[DemoGenerationResult] = []
        
        # Ensure output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize providers
        self._init_providers()
    
    def _init_providers(self):
        """Initialize video generation providers."""
        if "huggingface" in self.config.providers:
            try:
                hf_config = HFVideoConfig(
                    model=self.config.hf_model,
                    output_dir=os.path.join(self.config.output_dir, "huggingface"),
                    num_frames=24,
                    fps=8
                )
                self.providers["huggingface"] = HuggingFaceProvider(hf_config)
                logger.info("HuggingFace provider initialized")
            except Exception as e:
                logger.warning(f"Failed to init HuggingFace provider: {e}")
        
        if "veo" in self.config.providers:
            try:
                veo_config = VeoConfig(
                    project_id=self.config.veo_project_id,
                    output_dir=os.path.join(self.config.output_dir, "veo")
                )
                self.providers["veo"] = VeoProvider(veo_config)
                logger.info("Veo provider initialized")
            except Exception as e:
                logger.warning(f"Failed to init Veo provider: {e}")
    
    def get_shots_to_generate(self) -> List[Dict[str, Any]]:
        """Get list of shots to generate."""
        if self.config.shot_ids:
            return [s for s in DEMO_SHOTS if s["id"] in self.config.shot_ids]
        return DEMO_SHOTS
    
    async def generate_shot(
        self,
        shot: Dict[str, Any],
        provider_name: str
    ) -> DemoGenerationResult:
        """
        Generate a single shot using specified provider.
        
        Args:
            shot: Shot specification
            provider_name: Provider to use
        
        Returns:
            DemoGenerationResult
        """
        provider = self.providers.get(provider_name)
        
        if not provider:
            return DemoGenerationResult(
                shot_id=shot["id"],
                provider=provider_name,
                success=False,
                error=f"Provider {provider_name} not available"
            )
        
        logger.info(f"Generating {shot['id']} with {provider_name}...")
        
        try:
            # Generate video
            result = await provider.generate(
                prompt=shot["prompt"],
                duration=shot.get("duration_sec", 5),
                negative_prompt=shot.get("negative_prompt", "")
            )
            
            if result.success:
                return DemoGenerationResult(
                    shot_id=shot["id"],
                    provider=provider_name,
                    success=True,
                    video_path=result.video_path,
                    duration=result.duration,
                    prompt=shot["prompt"],
                    generation_time=result.generation_time
                )
            else:
                return DemoGenerationResult(
                    shot_id=shot["id"],
                    provider=provider_name,
                    success=False,
                    error=result.error,
                    prompt=shot["prompt"]
                )
                
        except Exception as e:
            logger.error(f"Error generating {shot['id']}: {e}")
            return DemoGenerationResult(
                shot_id=shot["id"],
                provider=provider_name,
                success=False,
                error=str(e),
                prompt=shot["prompt"]
            )
    
    async def generate_all(self) -> List[DemoGenerationResult]:
        """
        Generate all shots for the demo.
        
        Returns:
            List of generation results
        """
        shots = self.get_shots_to_generate()
        results = []
        
        for shot in shots:
            for provider_name in self.config.providers:
                result = await self.generate_shot(shot, provider_name)
                results.append(result)
                self.results.append(result)
                
                # Log result
                if result.success:
                    logger.info(f"✓ {shot['id']} ({provider_name}): {result.video_path}")
                else:
                    logger.error(f"✗ {shot['id']} ({provider_name}): {result.error}")
                
                # Small delay between generations
                await asyncio.sleep(2)
        
        return results
    
    def assemble_demo(self, results: List[DemoGenerationResult]) -> Optional[str]:
        """
        Assemble generated clips into final demo video.
        
        Args:
            results: Generation results
        
        Returns:
            Path to final video or None
        """
        # Get successful results
        successful = [r for r in results if r.success and r.video_path]
        
        if not successful:
            logger.error("No successful generations to assemble")
            return None
        
        logger.info(f"Assembling {len(successful)} clips...")
        
        # Sort by shot order
        shot_order = {s["id"]: i for i, s in enumerate(DEMO_SHOTS)}
        successful.sort(key=lambda r: shot_order.get(r.shot_id, 999))
        
        # Get video paths
        video_paths = [r.video_path for r in successful]
        
        # Concatenate
        try:
            output_path = self.config.final_video_path
            VideoOperations.concatenate(video_paths, output_path)
            logger.info(f"Demo assembled: {output_path}")
            
            # Add titles if requested
            if self.config.add_titles:
                self._add_titles(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to assemble demo: {e}")
            return None
    
    def _add_titles(self, video_path: str):
        """Add title overlays to the assembled video."""
        pipeline = VideoTextPipeline()
        
        # Create title track
        track = TextTrack(name="Titles")
        
        # Opening title
        track.add_text(
            "CineLang Meta-Demo",
            start_time=0,
            end_time=3,
            position=TextPosition.CENTER
        )
        
        # Scene labels
        track.add_text(
            "Scene 1: Introduction",
            start_time=0.5,
            end_time=3,
            position=TextPosition.BOTTOM_CENTER
        )
        
        # Try to add titles
        try:
            output_with_titles = video_path.replace(".mp4", "_titled.mp4")
            pipeline.add_tracks(video_path, [track], output_with_titles)
            
            # Replace original
            os.replace(output_with_titles, video_path)
            logger.info("Added title overlays")
            
        except Exception as e:
            logger.warning(f"Could not add titles: {e}")
    
    def save_manifest(self, results: List[DemoGenerationResult]):
        """Save generation manifest for reference."""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "config": {
                "providers": self.config.providers,
                "output_dir": self.config.output_dir
            },
            "demo_config": DEMO_CONFIG,
            "shots": DEMO_SHOTS,
            "results": [
                {
                    "shot_id": r.shot_id,
                    "provider": r.provider,
                    "success": r.success,
                    "video_path": r.video_path,
                    "duration": r.duration,
                    "generation_time": r.generation_time,
                    "error": r.error
                }
                for r in results
            ]
        }
        
        manifest_path = os.path.join(self.config.output_dir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Saved manifest: {manifest_path}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Run the complete demo generation pipeline.
        
        Returns:
            Summary dict with results
        """
        logger.info("=" * 60)
        logger.info("CineLang Demo Runner")
        logger.info("=" * 60)
        
        # Show configuration
        logger.info(f"Providers: {self.config.providers}")
        logger.info(f"Output: {self.config.output_dir}")
        
        # Check providers
        available = [p for p in self.config.providers if p in self.providers]
        if not available:
            logger.error("No providers available!")
            return {"success": False, "error": "No providers available"}
        
        logger.info(f"Available providers: {available}")
        
        # Generate all shots
        logger.info("\nGenerating shots...")
        results = await self.generate_all()
        
        # Summarize
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"\nGeneration complete: {successful} successful, {failed} failed")
        
        # Assemble if we have successful results
        final_video = None
        if successful > 0:
            final_video = self.assemble_demo(results)
        
        # Save manifest
        self.save_manifest(results)
        
        return {
            "success": successful > 0,
            "total_shots": len(results),
            "successful": successful,
            "failed": failed,
            "final_video": final_video,
            "manifest": os.path.join(self.config.output_dir, "manifest.json")
        }


# ============ CLI Interface ============

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the CineLang meta-demo generation"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["huggingface", "veo", "both"],
        default="huggingface",
        help="Video generation provider to use"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output/demo",
        help="Output directory"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="cerspense/zeroscope_v2_576w",
        help="HuggingFace model to use"
    )
    
    parser.add_argument(
        "--veo-project",
        help="Google Cloud project ID for Veo"
    )
    
    parser.add_argument(
        "--shot", "-s",
        action="append",
        help="Specific shot ID to generate (can be repeated)"
    )
    
    parser.add_argument(
        "--list-shots",
        action="store_true",
        help="List all shots in the demo"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available HuggingFace models"
    )
    
    return parser.parse_args()


def list_shots():
    """Print all shots in the demo."""
    print("\n📽️  CineLang Demo Shots")
    print("=" * 60)
    
    total_duration = 0
    for shot in DEMO_SHOTS:
        duration = shot.get("duration_sec", 5)
        total_duration += duration
        
        print(f"\n{shot['id']}")
        print(f"  Scene: {shot['scene']}")
        print(f"  Type: {shot['type']}")
        print(f"  Duration: {duration}s")
        print(f"  Prompt: {shot['prompt'][:80]}...")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {len(DEMO_SHOTS)} shots, {total_duration}s ({total_duration/60:.1f} min)")


def list_models():
    """Print available HuggingFace models."""
    print("\n🤗 Available HuggingFace Video Models")
    print("=" * 60)
    
    models = [
        ("cerspense/zeroscope_v2_576w", "Zeroscope v2 (fast, 6GB VRAM)"),
        ("cerspense/zeroscope_v2_XL", "Zeroscope v2 XL (high quality, 12GB)"),
        ("damo-vilab/text-to-video-ms-1.7b", "ModelScope T2V (8GB)"),
        ("guoyww/animatediff-motion-adapter-v1-5-2", "AnimateDiff (8GB)"),
        ("ByteDance/AnimateDiff-Lightning", "AnimateDiff Lightning (fast)"),
        ("THUDM/CogVideoX-2b", "CogVideoX 2B (16GB)"),
        ("stabilityai/stable-video-diffusion-img2vid-xt", "SVD-XT (image-to-video, 16GB)"),
    ]
    
    for model_id, desc in models:
        print(f"\n{model_id}")
        print(f"  {desc}")


async def main():
    """Main entry point."""
    args = parse_args()
    
    if args.list_shots:
        list_shots()
        return
    
    if args.list_models:
        list_models()
        return
    
    # Configure providers
    providers = []
    if args.provider == "both":
        providers = ["huggingface", "veo"]
    else:
        providers = [args.provider]
    
    # Create config
    config = DemoRunnerConfig(
        output_dir=args.output,
        providers=providers,
        hf_model=args.model,
        veo_project_id=args.veo_project,
        shot_ids=args.shot
    )
    
    # Run demo
    runner = DemoRunner(config)
    result = await runner.run()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Demo Generation Summary")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Shots: {result['successful']}/{result['total_shots']} successful")
    
    if result.get("final_video"):
        print(f"Final Video: {result['final_video']}")
    
    print(f"Manifest: {result['manifest']}")


if __name__ == "__main__":
    asyncio.run(main())
