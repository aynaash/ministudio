"""
ContextBytes: Human & Machine Harmony (Brand Story)
==================================================
A 60-second Ghibli-style cinematic introduction to ContextBytes.
Demonstrates:
- Identity Grounding 2.0 for Emma and David
- Complex environment transitions (Cold Lab -> Magical Garden -> Cloud Library)
- Particle system synchronization (Teal knowledge threads)
- High-warmth Studio TTS integration
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
# CHARACTERS - Identity Grounding 2.0 (Master Portraits)
# ============================================================================

EMMA = Character(
    name="Emma",
    # IDENTITY: Persistent Ghibli Heroine features - The Researcher
    identity={
        "hair": "short chestnut brown bob, hand-drawn texture with soft bangs",
        "eyes": "large inquisitive amber eyes with detailed catchlights",
        "face": "soft round Shinkai-style face, expressive subtle smile",
        "build": "slender, wearing a high-quality cerulean blue wool sweater",
        "aesthetic": "painterly Ghibli protagonist, cinematic digital painting"
    },
    # Master Reference for Consistency
    visual_anchor_path="path/to/emma_master_portrait.jpg",
    current_state={
        "clothing": "cerulean blue winter sweater with high neck",
        "expression": "overwhelmed but curious"
    },
    voice_id="en-US-Studio-O",  # Warm, high-warmth studio narrator
    voice_profile={"style": "warm", "pitch": 0.5}
)

DAVID = Character(
    name="David",
    # IDENTITY: The Intellectual Professional
    identity={
        "hair": "neatly groomed short onyx black hair",
        "eyes": "deep intelligent dark eyes, scholarly focus",
        "face": "focused angular features, clean-shaven",
        "glasses": "minimalist silver-rimmed circular glasses",
        "aesthetic": "refined professional Ghibli style"
    },
    visual_anchor_path="path/to/david_master_portrait.jpg",
    current_state={
        "clothing": "charcoal grey oxford shirt and a thick forest green scarf",
        "expression": "searching for clarity"
    },
    voice_id="en-GB-Neural2-B",
    voice_profile={"style": "narrative", "pitch": -0.5}
)

ORB = Character(
    name="The ContextKeeper Orb",
    identity={
        "form": "a levitating orb of liquid golden light, tennis-ball size",
        "glow": "radiates #D4AF37 golden pulses and floating motes",
        "texture": "ethereal, translucent golden core"
    }
)

# ============================================================================
# ENVIRONMENTS - From Digital Noise to Cloud Wisdom
# ============================================================================

DATA_ABYSS = Environment(
    location="The Blue Digital Maze",
    identity={"architecture": "endless floating screens and neon data streams"},
    current_context={
        "lighting": "cold cinematic teal and glitchy white light",
        "atmosphere": "claustrophobic, overwhelming, flickering"
    }
)

GHIBLI_ATELIER = Environment(
    location="The Knowledge Garden Study",
    identity={
        "architecture": "arched mahogany bookshelves, high ceilings, spiral stairs"},
    current_context={
        "lighting": "warm afternoon sun with visible dust motes (Tyndall effect)",
        "atmosphere": "magical, painterly, deep academic peace"
    }
)

CLOUD_STRATOSPHERE = Environment(
    location="Infinite Library above the Clouds",
    identity={"architecture": "crystalline glass shelves floating in the sky"},
    current_context={
        "lighting": "Majestic Shinkai sunset: vibrant purples, golds, and pinks",
        "atmosphere": "transcendental, awe-inspiring, infinite"
    }
)

# ============================================================================
# STYLE DNA - The "WOW" Factor (Shinkai x Ghibli)
# ============================================================================

GHIBLI_AWE_2_0 = StyleDNA(
    traits={
        "visual_style": "Studio Ghibli hand-painted backgrounds",
        "lighting_style": "Makoto Shinkai vibrant lens flares and glowing edges",
        "color_palette": "Deep teals (#008080) transitioning to Master Gold (#D4AF37)",
        "mood": "Cinematic intellectual breakthrough"
    },
    references=["Spirited Away", "Your Name", "The Garden of Words"]
)


async def create_brand_story(sample_only: bool = False):
    print("🎬 Starting Production: ContextBytes Brand Story (PREMIUM v2.0)...")

    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    scene = SceneConfig(
        concept="From Chaos to Mastery: The ContextBytes Promise",
        mood="Awe-inspiring and Harmonious",
        characters={"Emma": EMMA, "David": DAVID, "The Orb": ORB},
        shots=[
            # Shot 1: The Descent (00-08s)
            ShotConfig(
                shot_type=ShotType.CU,
                environment=DATA_ABYSS,
                action="Close-up on Emma's eyes. Hundreds of flickering icons reflect in her amber pupils as she looks exhausted. The camera pans to her messy desk.",
                narration="In a world of infinite data, we've lost the one thing that makes it wisdom: Context.",
                duration_seconds=8
            ),

            # Shot 2: The Fragmented Search (08-16s)
            ShotConfig(
                shot_type=ShotType.MS,
                environment=GHIBLI_ATELIER,
                action="David stares at a mountain of books, rubbing his temples. A tiny spark of gold, the Orb, begins to swell with light in the dark corner behind him.",
                narration="Fragments of thoughts, disconnected ideas... we're all just searching for the threads that bind them together.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 3: The Weaver (16-24s)
            ShotConfig(
                shot_type=ShotType.MS,
                environment=GHIBLI_ATELIER,
                action="The Orb pulses brilliantly. Vibrant teal light threads emerge, physically weaving between a book in Emma's hand and a video on David's iPad.",
                narration="Meet the ContextKeeper. It doesn't just store; it understands. It finds the invisible weave of your learning journey.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 4: The Bloom (24-32s)
            ShotConfig(
                shot_type=ShotType.WS,
                environment=GHIBLI_ATELIER,
                action="The wooden study transforms. Glowing vines of bioluminescent data grow like vines around the desk. Emma's face lights up with pure Ghibli-wonder.",
                narration="Turning your digital workspace into a living, breathing garden of insight. From a single whisper to a total mastery.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 5: The Ascent (32-40s)
            ShotConfig(
                shot_type=ShotType.WS,
                environment=CLOUD_STRATOSPHERE,
                action="Emma and David walk across a glass floor in the clouds. Thousands of golden nodes (The Knowledge Graph) pulse in harmony under a Shinkai sunset.",
                narration="It scales with your ambition. Whether you're a seeker or a pioneer—ContextBytes is your cognitive partner.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 6: Final Harmony (40-48s)
            ShotConfig(
                shot_type=ShotType.MS,
                environment=CLOUD_STRATOSPHERE,
                action="Emma and David look into the camera and smile. The Orb flies forward, its light engulfing the screen and morphing into the ContextBytes logo.",
                narration="Deep simplicity. Modern intelligence. This is your Context, mastered. Welcome to ContextBytes.",
                duration_seconds=8,
                continuity_required=True
            )
        ]
    )

    if sample_only:
        print("🔍 SAMPLE MODE: Generating first shot only.")
        scene.shots = [scene.shots[0]]

    # Production Config
    config = VideoConfig(
        style_dna=GHIBLI_AWE_2_0,
        output_dir="./contextbytes_production",
        aspect_ratio="16:9",
        negative_prompt="3d render, CGI, grainy, realistic photo, distorted face, inconsistent hair"
    )

    # Run production
    result = await orchestrator.generate_production(
        scene=scene,
        base_config=config,
        output_filename="contextbytes_brand_story.mp4"
    )

    if result["success"]:
        print(f"✨ SUCCESS! Final brand story saved to: {result['local_path']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="ContextBytes Brand Story Generator")
    parser.add_argument("--sample", action="store_true",
                        help="Generate only the first shot")
    args = parser.parse_args()

    asyncio.run(create_brand_story(sample_only=args.sample))
