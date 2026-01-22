"""
ContextBytes Ghibli Video Studio - Unified Demo
=============================================
Demonstrates the integration of Vertex AI, Google TTS, and S3
to generate a high-fidelity Ghibli-style brand story.
"""

import asyncio
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from ministudio.orchestrator import VideoOrchestrator
from ministudio.providers.vertex_ai import VertexAIProvider
from ministudio.config import VideoConfig, SceneConfig, ShotConfig, ShotType
from ministudio.styles.ghibli import GHIBLI_CONFIG, EMMA, DAVID, ORB

# Load environment
load_dotenv()


async def generate_brand_story(sample_only: bool = False, upload: bool = False):
    print("🎬 Starting Ghibli Brand Story Production...")

    # 1. Initialize Provider and Orchestrator
    # Note: VertexAIProvider will automatically load credentials from env
    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    # 2. Define the Brand Story Scene based on User Request
    scene = SceneConfig(
        concept="ContextKeeper Brand Story",
        mood="Emotional, Intellectual, Ghibli Awe",
        shots=[
            ShotConfig(
                shot_type=ShotType.CU,
                action="Emma (Ghibli heroine) looking overwhelmed at a desk. Hundreds of flickering digital screens reflect in her eyes. The room is cold, blue-toned.",
                narration="In a world of infinite data, we've lost the one thing that makes it wisdom: Context.",
                duration_seconds=8,
                characters={"Emma": EMMA}
            ),
            ShotConfig(
                shot_type=ShotType.MS,
                action="David (focused student) staring at a pile of books and a Tablet. He sighs. A small, dim golden light (The Orb) begins to flicker in the corner of his study.",
                narration="Fragments of thoughts, disconnected ideas... we're all just searching for the threads that bind them together.",
                duration_seconds=8,
                characters={"David": DAVID}
            ),
            ShotConfig(
                shot_type=ShotType.MS,
                action="The Orb pulses vibrant gold. It floats between Emma and David. Suddenly, teal light threads connect a physical book Emma is holding to a video playing on David's screen.",
                narration="Meet the ContextKeeper. It doesn't just store; it understands. It finds the invisible weave of your learning journey.",
                duration_seconds=8,
                characters={"Emma": EMMA, "David": DAVID, "Orb": ORB}
            ),
            ShotConfig(
                shot_type=ShotType.WS,
                action="The study transforms. Glowing knowledge constellations grow like vines around the desk. Emma's face lights up with wonder; she's grinning as she sees the connections.",
                narration="Turning your digital workspace into a living, breathing garden of insight. From a single whisper to a total mastery.",
                duration_seconds=8,
                characters={"Emma": EMMA}
            ),
            ShotConfig(
                shot_type=ShotType.WS,
                action="A massive, beautiful Ghibli-style library in the clouds. Thousands of golden nodes (The Knowledge Graph) pulse in harmony. Emma and David are seen walking through it, empowered.",
                narration="It scales with your ambition. Whether you're a curious seeker or a pioneer of progress—ContextBytes is your cognitive partner.",
                duration_seconds=8,
                characters={"Emma": EMMA, "David": DAVID}
            ),
            ShotConfig(
                shot_type=ShotType.MS,
                action="Emma and David look toward the screen, smiling. The Orb floats into the camera, morphing into the ContextBytes logo. Warm, golden sunset lighting (Golden Hour).",
                narration="Deep simplicity. Modern intelligence. This is your Context, mastered. Welcome to ContextBytes.",
                duration_seconds=8,
                characters={"Emma": EMMA, "David": DAVID, "Orb": ORB}
            )
        ]
    )

    if sample_only:
        print("🔍 Running in SAMPLE mode: Only generating the first shot.")
        scene.shots = [scene.shots[0]]

    # 3. Configure the Production
    config = GHIBLI_CONFIG
    config.output_dir = "./ghibli_production"

    # 4. Run the Orchestrator
    production_result = await orchestrator.generate_production(
        scene=scene,
        base_config=config,
        output_filename="contextkeeper_brand_story.mp4",
        upload_to_s3=upload
    )

    if production_result["success"]:
        print("\nPRODUCTION COMPLETE!")
        print(f"📍 Local Path: {production_result['local_path']}")
        if "s3_url" in production_result:
            print(f"🔗 S3 URL: {production_result['s3_url']}")
    else:
        print("\n❌ PRODUCTION FAILED")
        for i, res in enumerate(production_result["results"]):
            if not res.success:
                print(f"  Shot {i+1} failed: {res.error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ContextBytes Ghibli Video Studio - Unified Demo")
    parser.add_argument("--sample", action="store_true",
                        help="Only generate the first shot")
    parser.add_argument("--upload", action="store_true",
                        help="Upload final video to S3")
    args = parser.parse_args()

    asyncio.run(generate_brand_story(
        sample_only=args.sample, upload=args.upload))
