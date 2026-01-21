"""
Consistent Story Demo - Quantum Mechanics Masterclass
=====================================================
Demonstrates the refined Global/Local state architecture for:
- Absolute character identity persistence (face, hair, eyes)
- Stationary background architecture vs. transient context
- Character-to-voice mapping and visual synchronization
- Explicit sequential segment generation

Story: A Grandfather explaining the 'Double-Slit Experiment' to his Granddaughter.
"""

import asyncio
from pathlib import Path
from ministudio.orchestrator import VideoOrchestrator
from ministudio.providers.vertex_ai import VertexAIProvider
from ministudio.config import (
    VideoConfig, SceneConfig, ShotConfig, ShotType,
    Character, Environment, StyleDNA
)

# ============================================================================
# GLOBAL IDENTITY DEFINITIONS - These are "anchored" in the state machine
# ============================================================================

GRANDFATHER = Character(
    name="Grandfather Elias",
    # IDENTITY: This stays identical in every single shot
    identity={
        "hair_style": "thick white messy hair and matching short white beard",
        "hair_color": "snow white",
        "eye_color": "bright wise blue eyes",
        "skin_tone": "fair with wrinkles of experience",
        "face_shape": "kind oval face with high cheekbones",
        "height_build": "slight, dignified posture"
    },
    # Master reference portrait
    visual_anchor_path="path/to/grandfather_portrait_anchor.jpg",
    # LOCAL STATE: Can change per scene (e.g., different clothes)
    current_state={
        "clothing": "a cozy moss-green wool cardigan over a white collared shirt",
        "posture": "sitting upright in an antique mahogany armchair"
    },
    voice_id="en-US-Neural2-D",
    voice_profile={
        "style": "warm and academic",
        "pitch": -2.0
    }
)

GRANDDAUGHTER = Character(
    name="Young Maya",
    identity={
        "hair_style": "long dark chestnut hair in a neat ponytail",
        "hair_color": "chestnut brown",
        "eye_color": "large inquisitive dark brown eyes",
        "skin_tone": "olive",
        "face_shape": "round youthful face",
        "height_build": "small 8-year-old frame"
    },
    visual_anchor_path="path/to/maya_portrait_anchor.jpg",  # Master reference portrait
    current_state={
        "clothing": "a simple yellow sunshine t-shirt and blue jeans",
        "posture": "sitting cross-legged on a plush vintage rug"
    },
    voice_id="en-US-Neural2-F",
    voice_profile={
        "style": "bright and curious",
        "pitch": 2.0
    }
)

# ============================================================================
# ENVIRONMENT IDENTITY - The "Global" Architecture vs "Local" context
# ============================================================================

SCIENTIFIC_STUDY = Environment(
    location="Old Scientific Study",
    identity={
        "architecture_style": "Victorian-era logic with oak paneling",
        "fixed_elements": "floor-to-ceiling bookshelves, a large arched window on the left",
        "base_color_palette": "warm browns, brass, and velvet greens"
    },
    current_context={
        "lighting": "soft amber glow from a desk lamp mixing with blue dusk light",
        "time_of_day": "twilight",
        "atmosphere": "quiet, scholarly, yet intimate"
    }
)

# ============================================================================
# STYLE DNA
# ============================================================================

PHOTOREAL_CINEMATIC = StyleDNA(
    traits={
        "aesthetic": "hyper-photorealistic cinematic drama",
        "visual_style": "shot on 35mm film, shallow depth of field",
        "color_grading": "warm highlights, deep rich shadows"
    },
    references=["National Geographic photography",
                "Cinematic academic portraits"]
)


async def generate_consistent_production(sample_only: bool = False):
    print("🎬 Starting Consistent Production: 'The Double-Slit Mystery'...")

    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    # Define the 1-minute educational TikTok story
    # The orchestrator will use the State Machine to ensure identity persistence
    scene = SceneConfig(
        concept="Quantum Mystery",
        mood="Awe and Wonder",
        characters={
            "Grandfather Elias": GRANDFATHER,
            "Young Maya": GRANDDAUGHTER
        },
        environment=SCIENTIFIC_STUDY,
        shots=[
            # Shot 1: The Hook
            ShotConfig(
                shot_type=ShotType.MS,
                action="Maya looks at a physics diagram on the table. Elias watches her with a warm smile.",
                dialogue="Maya: Grandpa, why do the particles act like waves?",
                duration_seconds=8
            ),

            # Shot 2: The Core Concept
            ShotConfig(
                shot_type=ShotType.CU,
                action="Close-up on Elias's face. He raises a finger, his eyes twinkling in the lamplight. His lips move in perfect sync.",
                dialogue="Elias: Because in the quantum world, Young Maya, things don't choose where they are until we look at them.",
                duration_seconds=8,
                continuity_required=True  # Frame-to-frame continuity
            ),

            # Shot 3: The Mystery
            ShotConfig(
                shot_type=ShotType.MS,
                action="Maya leans forward, her brow furrowed in concentration. Elias shows her a small laser pointer.",
                narration="It's called the Double-Slit experiment. The greatest mystery of the small.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 4: Transformation (Same Scene, new action)
            ShotConfig(
                shot_type=ShotType.WS,
                action="Wide shot of the study. Elias stands up, gesturing toward the arched window where stars are appearing.",
                dialogue="Elias: The universe is shy. It hides its secrets when we're not watching.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 5: Conclusion
            ShotConfig(
                shot_type=ShotType.MS,
                action="Maya looks at the window, then back at Elias, smiling widely. He puts a hand on her shoulder.",
                dialogue="Maya: I think I'm starting to see the invisible weave, Grandpa!",
                duration_seconds=8,
                continuity_required=True
            )
        ]
    )

    if sample_only:
        print("🔍 SAMPLE MODE: Generating first shot to verify identity anchors.")
        scene.shots = [scene.shots[0]]

    # Configure the Production
    config = VideoConfig(
        style_dna=PHOTOREAL_CINEMATIC,
        output_dir="./consistent_story_production",
        aspect_ratio="9:16",  # TikTok Format
        negative_prompt="blurry, inconsistent hair, changing clothes, disappearing beard, morphing background"
    )

    # Run the Orchestrator
    # Internal: Next generation will use 'identity' keys to force consistency
    production_result = await orchestrator.generate_production(
        scene=scene,
        base_config=config,
        output_filename="double_slit_mystery.mp4"
    )

    if production_result["success"]:
        print("\n✅ CONSISTENT PRODUCTION COMPLETE!")
        print(f"📍 Final Video: {production_result['local_path']}")
    else:
        print("\n❌ PRODUCTION FAILED")
        for i, res in enumerate(production_result["results"]):
            if not res.success:
                print(f"  Shot {i+1} failed: {res.error}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Ministudio Consistent Story Demo")
    parser.add_argument("--sample", action="store_true",
                        help="Generate only the first shot")
    args = parser.parse_args()

    asyncio.run(generate_consistent_production(sample_only=args.sample))
