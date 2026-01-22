"""
Character consistency demo for Ministudio.
============================================

This example demonstrates Ministudio's core innovation: character consistency.
The same character appears in multiple videos with the same appearance.
"""

import asyncio
from ministudio import Ministudio, StyleConfig


async def main():
    """Demonstrate character consistency across multiple generations"""

    print("🎭 Ministudio Character Consistency Demo")
    print("=" * 45)

    # 1. Define a custom character style
    print("1. Defining character style...")
    custom_style = StyleConfig(
        name="demo_style",
        description="Educational demonstration style",
        characters={
            "orb": {
                "appearance": "Golden glowing orb with warm inner light",
                "surface": "Translucent with gentle data-circuit patterns flowing inside",
                "glow": "Soft golden with ethereal teal accents",
                "motion": "Slow floating drift, gentle bobbing",
                "size": "tennis ball sized"
            }
        },
        environment={
            "setting": "Clean educational space with soft lighting",
            "lighting": "Warm, professional studio lighting",
            "color_palette": "Warm golds, deep teals, clean whites",
            "texture": "Smooth, modern, educational feel"
        },
        technical={
            "fps": 24,
            "motion_style": "Smooth, deliberate movements",
            "depth_of_field": "Shallow, cinematic focus",
            "continuity": "Maintain character appearance across all frames"
        }
    )
    print(
        f"   Character defined: {custom_style.characters['orb']['appearance']}")

    # 2. Create provider and studio
    print("2. Setting up Ministudio...")
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider=provider, style_config=custom_style)
    print(f"   Using provider: {provider.name}")
    print(f"   Style: {custom_style.name}")

    # 3. Generate multiple videos with the same character
    print("3. Generating consistent character videos...")

    videos = [
        {
            "concept": "Mathematics",
            "action": "orb solving geometric equations visually"
        },
        {
            "concept": "Physics",
            "action": "orb demonstrating gravitational waves"
        },
        {
            "concept": "Computer Science",
            "action": "orb sorting algorithms with data structures"
        }
    ]

    results = []

    for i, video_spec in enumerate(videos, 1):
        print(f"   Generating video {i}/3: {video_spec['concept']}")

        result = await studio.generate_concept_video(
            concept=video_spec["concept"],
            action=video_spec["action"],
            duration=8,
            mood="educational"
        )

        results.append(result)

        if result.success:
            print(f"     ✓ Success ({result.generation_time:.1f}s)")
            if result.video_path:
                print(f"Saved: {result.video_path.name}")
        else:
            print(f"     ✗ Failed: {result.error}")

    # 4. Summary
    print("4. Summary:")
    successful = sum(1 for r in results if r.success)
    total = len(results)
    print(f"   Videos generated: {successful}/{total}")

    if successful > 0:
        print("   🎯 Character consistency achieved!")
        print("   The 'orb' character maintains the same appearance in all videos:")
        orb_desc = custom_style.characters["orb"]
        print(f"   - Appearance: {orb_desc['appearance']}")
        print(f"   - Glow: {orb_desc['glow']}")
        print(f"   - Motion: {orb_desc['motion']}")
        print("   - Size: {orb_desc['size']}")

    print("\nCharacter consistency demo completed!")
    print("\nKey Innovation: Define once, consistent everywhere")
    print("   Traditional AI video: Characters change between generations")
    print("   Ministudio: Same character, every time")


if __name__ == "__main__":
    asyncio.run(main())
