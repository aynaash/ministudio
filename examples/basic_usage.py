"""
Basic usage example for Ministudio.
=========================================

This example shows how to generate a single video using the mock provider.
No API keys required - perfect for getting started.
"""

import asyncio
from ministudio import Ministudio


async def main():
    """Generate a basic video using Ministudio"""

    print("🚀 Ministudio Basic Usage Example")
    print("=" * 40)

    # 1. Create a provider
    # Use mock provider for testing (no API keys needed)
    print("1. Creating mock provider...")
    provider = Ministudio.create_provider("mock")
    print(f"   Provider: {provider.name}")

    # 2. Create Ministudio instance
    print("2. Creating Ministudio instance...")
    studio = Ministudio(provider=provider)
    print(f"   Output directory: {studio.output_dir}")

    # 3. Generate a video
    print("3. Generating video...")
    concept = "Machine Learning"
    action = "orb sorting colorful data points"

    result = await studio.generate_concept_video(
        concept=concept,
        action=action,
        duration=8
    )

    # 4. Check results
    print("4. Results:")
    print(f"   Success: {result.success}")
    print(f"   Provider used: {result.provider}")
    print(".2f")
    print(f"   Video generated: {result.has_video}")

    if result.success and result.video_path:
        print(f"   Video saved to: {result.video_path}")
        print(f"   File size: {result.video_path.stat().st_size} bytes")
    elif result.error:
        print(f"   Error: {result.error}")

    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
