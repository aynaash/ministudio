"""
MiniStudio Simple Builder

Easy-to-use interface for non-technical users.
Just describe what you want, and we handle the rest!

Example:
    from ministudio.simple_builder import generate_video_from_description
    
    description = \"\"\"
    A scientist in a lab coat discovers a glowing orb.
    She looks amazed and reaches towards it.
    The camera slowly zooms in.
    Duration: 10 seconds
    Style: cinematic with dramatic lighting
    \"\"\"
    
    result = generate_video_from_description(description)
    print(f"Video generated: {result.video_path}")
"""

import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from .config import ShotConfig, VideoConfig, ProviderConfig
from .providers import create_provider, list_providers, BaseVideoProvider
from .interfaces import VideoGenerationRequest, VideoGenerationResult
from .orchestrator import VideoOrchestrator


@dataclass
class SimpleVideoRequest:
    """Simple request from non-technical user"""
    description: str
    duration_seconds: int = 8
    style: str = "cinematic"
    character_names: Optional[Dict[str, str]] = None  # {"Emma": "emma.jpg"}
    provider: str = "auto"  # "vertex_ai", "huggingface", "local", or "auto"


class SimpleBuilder:
    """Build video configs from simple descriptions"""
    
    STYLE_MAPPING = {
        "cinematic": "cinematic, dramatic lighting, professional cinematography",
        "cyberpunk": "cyberpunk, neon colors, dystopian, high tech",
        "ghibli": "Studio Ghibli style, anime, hand-drawn aesthetic",
        "realistic": "photorealistic, natural lighting, documentary style",
        "fantasy": "fantasy, magical, epic, adventurous",
        "horror": "horror, dark, suspenseful, atmospheric",
        "comedy": "funny, lighthearted, comedic, playful",
    }
    
    @staticmethod
    def parse_description(description: str) -> Dict[str, Any]:
        """
        Parse simple user description into config parameters.
        Extracts action, duration, style, etc.
        """
        description_lower = description.lower()
        
        # Extract duration if mentioned
        duration = 8  # default
        if "second" in description_lower:
            for word in description.split():
                if word.isdigit():
                    duration = min(int(word), 60)  # Max 60 seconds
                    break
        
        # Detect style
        style = "cinematic"  # default
        for style_key in SimpleBuilder.STYLE_MAPPING.keys():
            if style_key in description_lower:
                style = style_key
                break
        
        return {
            "action": description.split("Duration:")[0].strip(),
            "duration": duration,
            "style": style,
        }
    
    @staticmethod
    def create_shot_config(request: SimpleVideoRequest) -> ShotConfig:
        """Convert simple request to ShotConfig"""
        parsed = SimpleBuilder.parse_description(request.description)
        
        # Build style string with enhancements
        style_text = SimpleBuilder.STYLE_MAPPING.get(
            request.style,
            request.style
        )
        
        # Combine action with style
        enhanced_action = f"{parsed['action']}. Style: {style_text}"
        
        return ShotConfig(
            action_description=enhanced_action,
            characters=request.character_names or {},
            duration_seconds=parsed["duration"],
            style=request.style,
        )
    
    @staticmethod
    async def get_provider(provider_name: str = "auto") -> BaseVideoProvider:
        """
        Get provider based on user preference.
        
        "auto" tries to detect best available provider.
        """
        if provider_name == "auto":
            # Use unified provider factory with auto-detection
            try:
                provider = create_provider()
                providers = list_providers()
                # Find which one was selected
                for name, info in providers.items():
                    if info.get("configured"):
                        print(f"✅ Using {name} for generation")
                        break
                return provider
            except Exception as e:
                raise RuntimeError(
                    f"No video provider available: {e}\n"
                    "Please set up one: Vertex AI, Local Model, etc.\n"
                    "See: docs/configuration_and_secrets.md"
                )
        else:
            # Use specific provider
            try:
                provider = create_provider(provider_name)
                print(f"✅ Using {provider_name} for generation")
                return provider
            except Exception as e:
                raise ValueError(f"Provider {provider_name} not available: {e}")


async def generate_video_from_description(
    description: str,
    provider: str = "auto",
    character_names: Optional[Dict[str, str]] = None,
) -> VideoGenerationResult:
    """
    Generate a video from a simple text description.
    
    Args:
        description: What you want to generate (can include duration, style)
        provider: Which provider to use ("vertex_ai", "huggingface", "local", or "auto")
        character_names: Optional dict of character names to visual anchors
    
    Returns:
        VideoGenerationResult with generated video
    
    Example:
        result = await generate_video_from_description(
            \"\"\"
            A scientist discovers a glowing orb in the lab.
            The camera zooms in dramatically.
            Duration: 10 seconds
            Style: cinematic
            \"\"\",
            provider="auto"
        )
        print(f"Video saved to: {result.video_path}")
    """
    # Parse user input
    request = SimpleVideoRequest(
        description=description,
        character_names=character_names,
        provider=provider,
    )
    
    # Create config
    shot_config = SimpleBuilder.create_shot_config(request)
    
    # Get provider
    video_provider = await SimpleBuilder.get_provider(request.provider)
    
    # Create orchestrator
    orchestrator = VideoOrchestrator(video_provider)
    
    # Generate
    print(f"🎬 Generating video...")
    print(f"   Action: {shot_config.action_description[:60]}...")
    print(f"   Duration: {shot_config.duration_seconds}s")
    print(f"   Provider: {video_provider.name}")
    
    result = await orchestrator.generate_shot(shot_config)
    
    print(f"✅ Video generated!")
    return result


def generate_video(
    description: str,
    provider: str = "auto",
    character_names: Optional[Dict[str, str]] = None,
) -> VideoGenerationResult:
    """
    Synchronous wrapper for generate_video_from_description.
    
    Perfect for scripts and non-async contexts.
    
    Example:
        result = generate_video(
            \"A wizard casts a spell. Duration: 8 seconds. Style: fantasy\"
        )
    """
    return asyncio.run(
        generate_video_from_description(
            description=description,
            provider=provider,
            character_names=character_names,
        )
    )


# ============================================================================
# TEMPLATES: Pre-built scenarios for quick start
# ============================================================================

TEMPLATES = {
    "sci-fi-lab": """
    A scientist in a futuristic lab discovers a mysterious glowing orb.
    She looks amazed and reaches towards it.
    The camera slowly zooms in.
    Duration: 10 seconds
    Style: cinematic
    """,
    
    "fantasy-quest": """
    A brave warrior stands at the edge of a magical forest.
    She draws her sword as mysterious lights appear.
    The camera pans to reveal an ancient castle.
    Duration: 12 seconds
    Style: fantasy
    """,
    
    "cyberpunk-city": """
    A hacker in a neon-lit room stares at holographic screens.
    Futuristic code and data streams surround them.
    The camera zooms through the digital landscape.
    Duration: 8 seconds
    Style: cyberpunk
    """,
    
    "nature-journey": """
    A peaceful waterfall in a lush forest.
    Birds fly through the canopy as sunlight filters through.
    The camera reveals a hidden cave behind the water.
    Duration: 10 seconds
    Style: realistic
    """,
    
    "comedy-moment": """
    A character slips on a banana peel and tumbles hilariously.
    Friends laugh in the background.
    Everything is silly and exaggerated.
    Duration: 6 seconds
    Style: comedy
    """,
}


async def generate_from_template(template_name: str, provider: str = "auto"):
    """
    Generate video from a pre-built template.
    
    Available templates:
    - sci-fi-lab
    - fantasy-quest
    - cyberpunk-city
    - nature-journey
    - comedy-moment
    
    Example:
        result = await generate_from_template("sci-fi-lab")
    """
    if template_name not in TEMPLATES:
        raise ValueError(
            f"Unknown template: {template_name}\n"
            f"Available: {', '.join(TEMPLATES.keys())}"
        )
    
    description = TEMPLATES[template_name]
    return await generate_video_from_description(description, provider=provider)


# ============================================================================
# INTERACTIVE MODE: Walk user through setup
# ============================================================================

def interactive_setup():
    """
    Interactive setup for non-technical users.
    Walks through video generation step-by-step.
    """
    print("\n" + "="*60)
    print("🎬 MiniStudio - Easy Video Generation")
    print("="*60)
    
    # Step 1: Get description
    print("\n📝 Describe what you want to generate:")
    print("(Include duration and style if you want, e.g., '10 seconds, cyberpunk')")
    description = input("\nYour description: ").strip()
    
    if not description:
        print("❌ Description cannot be empty!")
        return
    
    # Step 2: Choose provider
    print("\n🔧 Which provider would you like to use?")
    print("  1. Auto (we'll pick the best available)")
    print("  2. Vertex AI (cloud, high quality)")
    print("  3. Hugging Face (flexible, open-source)")
    print("  4. Local Model (free, private)")
    
    choice = input("\nChoose (1-4, default 1): ").strip() or "1"
    provider_map = {
        "1": "auto",
        "2": "vertex_ai",
        "3": "huggingface",
        "4": "local",
    }
    provider = provider_map.get(choice, "auto")
    
    # Step 3: Confirm
    print("\n✨ Ready to generate!")
    print(f"   Description: {description[:50]}...")
    print(f"   Provider: {provider}")
    confirm = input("\nContinue? (y/n, default y): ").strip().lower() or "y"
    
    if confirm != "y":
        print("Cancelled!")
        return
    
    # Step 4: Generate
    print("\n⏳ Generating your video...")
    try:
        result = asyncio.run(
            generate_video_from_description(description, provider=provider)
        )
        print(f"\n✅ Success! Video saved to: {result.video_path}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check that you have credentials set up (.env file)")
        print("- See: docs/configuration_and_secrets.md")


if __name__ == "__main__":
    interactive_setup()
