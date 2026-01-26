"""
Simple Examples for Non-Technical Users

These are the EASIEST ways to generate videos with MiniStudio.
Just run them and describe what you want!
"""

import asyncio
from ministudio.simple_builder import (
    generate_video,
    generate_video_from_description,
    generate_from_template,
    interactive_setup,
    TEMPLATES,
)


# ============================================================================
# EXAMPLE 1: The Simplest Way - Just Describe It!
# ============================================================================

async def example_1_simplest():
    """Absolute easiest: just describe what you want"""
    
    description = """
    A lonely astronaut walks on the moon.
    They look up at Earth in the sky.
    The camera slowly pulls back to show the vast emptiness of space.
    Duration: 10 seconds
    Style: cinematic
    """
    
    result = await generate_video_from_description(description)
    print(f"✅ Video created: {result.video_path}")


# ============================================================================
# EXAMPLE 2: Using Pre-Built Templates
# ============================================================================

async def example_2_templates():
    """Use templates for common scenarios"""
    
    print("Available templates:")
    from ministudio.simple_builder import TEMPLATES
    for name in TEMPLATES.keys():
        print(f"  - {name}")
    
    # Generate from template
    result = await generate_from_template("sci-fi-lab")
    print(f"✅ Video created from template: {result.video_path}")


# ============================================================================
# EXAMPLE 3: Sync Version (Non-Async)
# ============================================================================

def example_3_sync():
    """Use synchronous API if you don't know async"""
    
    description = """
    A chef prepares a delicious meal in a professional kitchen.
    They taste the food with a satisfied smile.
    Duration: 8 seconds
    Style: realistic
    """
    
    # This works in regular Python scripts
    result = generate_video(description)
    print(f"✅ Video created: {result.video_path}")


# ============================================================================
# EXAMPLE 4: Specify a Different Provider
# ============================================================================

async def example_4_provider_choice():
    """Choose which provider to use"""
    
    description = "A robot dances to techno music. Duration: 6 seconds. Style: cyberpunk"
    
    # These all work the same way, just different providers:
    
    # Option A: Let MiniStudio pick the best one (recommended)
    result = await generate_video_from_description(description, provider="auto")
    
    # Option B: Use Vertex AI specifically
    # result = await generate_video_from_description(description, provider="vertex_ai")
    
    # Option C: Use Hugging Face
    # result = await generate_video_from_description(description, provider="huggingface")
    
    # Option D: Use Local Model
    # result = await generate_video_from_description(description, provider="local")
    
    print(f"✅ Video created: {result.video_path}")


# ============================================================================
# EXAMPLE 5: Interactive Mode (Best for Beginners)
# ============================================================================

def example_5_interactive():
    """Interactive setup - the most user-friendly way"""
    
    # This asks the user step-by-step what they want
    interactive_setup()


# ============================================================================
# EXAMPLE 6: Multiple Videos
# ============================================================================

async def example_6_multiple_videos():
    """Generate multiple videos in sequence"""
    
    descriptions = [
        "A wizard casts a fireball spell. Duration: 8 seconds. Style: fantasy",
        "A hacker types code. Duration: 6 seconds. Style: cyberpunk",
        "A dancer performs. Duration: 10 seconds. Style: cinematic",
    ]
    
    results = []
    for i, description in enumerate(descriptions, 1):
        print(f"\n🎬 Generating video {i}/{len(descriptions)}...")
        result = await generate_video_from_description(description)
        results.append(result)
        print(f"✅ Created: {result.video_path}")
    
    print(f"\n🎉 All {len(results)} videos created!")
    return results


# ============================================================================
# EXAMPLE 7: With Custom Characters
# ============================================================================

async def example_7_with_characters():
    """Generate video with specific characters"""
    
    description = """
    Emma the scientist discovers a glowing crystal.
    She examines it carefully with wonder.
    The crystal begins to glow brighter.
    Duration: 10 seconds
    Style: cinematic
    """
    
    result = await generate_video_from_description(
        description,
        character_names={
            "Emma": "emma_reference.jpg"  # Path to character reference image
        }
    )
    
    print(f"✅ Video created with character: {result.video_path}")


# ============================================================================
# EXAMPLE 8: Template Gallery
# ============================================================================

def example_8_show_templates():
    """Show all available templates"""
    
    print("\n" + "="*60)
    print("🎬 MiniStudio Template Gallery")
    print("="*60)
    
    from ministudio.simple_builder import TEMPLATES
    
    for name, description in TEMPLATES.items():
        print(f"\n📌 {name}:")
        print(f"   {description.strip()[:100]}...")
        print(f"   To use: await generate_from_template('{name}')")


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("""
    🎬 MiniStudio - Simple Examples
    
    Choose which example to run:
    1. Simplest way (just describe)
    2. Using templates
    3. Sync version (non-async)
    4. Different providers
    5. Interactive mode (recommended for beginners!)
    6. Multiple videos
    7. With custom characters
    8. Show all templates
    """)
    
    choice = input("Which example? (1-8, default 5): ").strip() or "5"
    
    examples = {
        "1": ("Simplest", example_1_simplest),
        "2": ("Templates", example_2_templates),
        "3": ("Sync", example_3_sync),
        "4": ("Providers", example_4_provider_choice),
        "5": ("Interactive", example_5_interactive),
        "6": ("Multiple", example_6_multiple_videos),
        "7": ("Characters", example_7_with_characters),
        "8": ("Show Templates", example_8_show_templates),
    }
    
    if choice not in examples:
        print(f"Unknown choice: {choice}")
        exit(1)
    
    name, func = examples[choice]
    print(f"\n▶️  Running: {name}\n")
    
    # Run example
    import inspect
    if inspect.iscoroutinefunction(func):
        asyncio.run(func())
    else:
        func()
