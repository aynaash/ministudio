"""
Command line interface for Ministudio.
"""

import os
import asyncio
import argparse
from .core import Ministudio


async def main():
    """Example usage"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ministudio AI Video Generator")

    parser.add_argument("--provider", choices=["vertex-ai", "mock", "local"],
                       default="mock", help="Video generation provider")
    parser.add_argument("--concept", type=str, help="Concept to visualize")
    parser.add_argument("--action", type=str, help="Action description")
    parser.add_argument("--duration", type=int, default=8, help="Duration in seconds")
    parser.add_argument("--output-dir", type=str, default="./ministudio_output",
                       help="Output directory")

    args = parser.parse_args()

    # Configure provider
    if args.provider == "vertex-ai":
        # Load from environment or config
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            print("Please set GCP_PROJECT_ID environment variable")
            return

        provider = Ministudio.create_provider(
            provider_type="vertex-ai",
            project_id=project_id
        )
    else:
        provider = Ministudio.create_provider(provider_type=args.provider)

    # Create Ministudio instance
    studio = Ministudio(
        provider=provider,
        output_dir=args.output_dir
    )

    # Generate video
    if args.concept and args.action:
        result = await studio.generate_concept_video(
            concept=args.concept,
            action=args.action,
            duration=args.duration
        )

        if result.success:
            print("✓ Video generated successfully!")
            print(f"  Provider: {result.provider}")
            print(".1f")
            if result.video_path:
                print(f"  Saved to: {result.video_path}")
        else:
            print(f"✗ Generation failed: {result.error}")
    else:
        print("Please provide --concept and --action arguments")
        print("Example: python -m ministudio --concept 'Quantum Physics' --action 'orb visualizing particles'")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
