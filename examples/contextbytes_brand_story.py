"""
ContextBytes: Human & Machine Harmony (Brand Story) - FLAGSHIP 60s+ EDITION
======================================================================
A cinematic introduction to ContextBytes with Dynamic Duration & Narrative Flow.
Story: Emma (Student) & David (Professional) find clarity via ContextKeeper.
"""

import asyncio
from pathlib import Path

from ministudio.orchestrator import VideoOrchestrator
from ministudio.providers.vertex_ai import VertexAIProvider
from ministudio.config import (
    VideoConfig, SceneConfig, ShotConfig, ShotType,
    Character, Environment, StyleDNA, Persona, DEFAULT_PERSONA,
    Cinematography, Camera, Color
)

# ============================================================================
# CINEMATOGRAPHY - Master Filmmaker Presets
# ============================================================================

PREMIUM_CINE = Cinematography(
    camera_behaviors={
        "chaos_pan": Camera(lens="24mm", aperture="f/4", movement_style="jittery handheld pan-through-clutter"),
        "discovery_macro": Camera(lens="100mm", aperture="f/2.8", movement_style="focus pull from screen to face"),
        "architecture_top": Camera(lens="35mm", aperture="f/8", movement_style="high-angle crane down"),
        "hero_infinite": Camera(lens="50mm", aperture="f/1.8", movement_style="slow push-in to subjects")
    },
    shot_composition_rules={
        "rule_of_thirds": True,
        "leading_lines": "towards the Knowledge Orb",
        "depth_layering": "foreground bokeh, midground subjects, background architecture"
    }
)

# ============================================================================
# CHARACTERS - Visual Anchor Links
# ============================================================================

EMMA = Character(
    name="Emma",
    identity={
        "hair": "short chestnut brown bob, hand-drawn texture with soft bangs",
        "eyes": "large inquisitive amber eyes with detailed catchlights",
        "face": "soft round Shinkai-style face, expressive subtle smile",
        # Absolute consistency lock
        "skin_tone": "fair porcelain with slight pink blush on cheeks",
        "build": "slender, wearing a high-quality cerulean blue wool sweater",
        "aesthetic": "painterly Ghibli protagonist, cinematic digital painting"
    },
    visual_anchor_path="c:/Users/USER/Music/ministudio/assets/references/emma_portrait.png",
    current_state={
        "clothing": "cerulean blue winter sweater, messy desk environment"},
    voice_id="en-US-Studio-O",  # Warm, welcoming female narrator
    voice_profile={"style": "narrative", "pitch": 0.5}
)

DAVID = Character(
    name="David",
    identity={
        "hair": "neatly groomed short onyx black hair",
        "eyes": "deep intelligent dark eyes, scholarly focus",
        "face": "focused angular features, clean-shaven",
        # Absolute consistency lock
        "skin_tone": "warm bronze skin with detailed hand-drawn shadows",
        "glasses": "minimalist silver-rimmed circular glasses",
        "aesthetic": "refined professional Ghibli style"
    },
    visual_anchor_path="c:/Users/USER/Music/ministudio/assets/references/david_portrait.png",
    current_state={
        "clothing": "charcoal grey corporate shirt, forest green scarf"}
)

Keeper = Character(
    name="The ContextKeeper",
    identity={
        "form": "a levitating orb of liquid golden light, tennis-ball size",
        "glow": "radiates #D4AF37 golden pulses and floating motes",
        "texture": "ethereal, translucent golden core"
    }
)

# ============================================================================
# ENVIRONMENTS - Chaos to Wisdom
# ============================================================================

CHAOTIC_DORM = Environment(
    location="Emma's Biology Dorm",
    identity={
        "architecture": "cluttered bookshelves, messy desktop, stacks of biology PDFs"},
    current_context={
        "lighting": "dim indoor light, blue glare from multiple computer screens",
        "atmosphere": "claustrophobic, overwhelming information overload",
        "time_of_day": "late night study session"
    },
    reference_images=[
        "c:/Users/USER/Music/ministudio/assets/references/data_abyss_bg.png"]
)

CORPORATE_MAZE = Environment(
    location="Modern Tech Office Lab",
    identity={
        "architecture": "glass walls, whiteboards filled with complex architecture diagrams"},
    current_context={
        "lighting": "slick fluorescent lighting, high-contrast shadows",
        "atmosphere": "dry, technical, professional overwhelm",
        "time_of_day": "busy afternoon"
    },
    reference_images=[
        # Anchor for David's office vibes
        "c:/Users/USER/Music/ministudio/assets/references/shinkai_stratosphere_bg.png"]
)

GITHUB_GARDEN = Environment(
    location="The Knowledge Garden Study",
    identity={
        "architecture": "arched mahogany bookshelves, high ceilings, spiral stairs"},
    current_context={
        "lighting": "warm afternoon sun with visible dust motes (Tyndall effect)",
        "atmosphere": "magical, painterly, deep academic peace",
        "time_of_day": "golden hour"
    },
    reference_images=[
        "c:/Users/USER/Music/ministudio/assets/references/ghibli_atelier_bg.png"]
)

STYLE_DNA = StyleDNA(
    traits={
        "visual_style": "Studio Ghibli hand-painted backgrounds",
        "lighting_style": "Makoto Shinkai vibrant lens flares and glowing edges",
        "color_palette": "Deep teals (#008080) transitioning to Master Gold (#D4AF37)",
        "brushwork": "Painterly, thick impasto textures on clouds",
        "detail_level": "Ultra-high, hyper-focused foregrounds"
    },
    references=["Spirited Away", "Your Name"]
)


async def create_brand_video():
    print("🎬 Starting FLAGSHIP Production: ContextBytes Brand Story (Dynamic Flow)...")

    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    scene = SceneConfig(
        concept="From Chaos to Human Wisdom",
        mood="Intellectual, Cinematic, Magical",
        characters={"Emma": EMMA, "David": DAVID, "Keeper": Keeper},
        shots=[
            # 1. Emma's Struggle (Demonstrates long narration splitting)
            ShotConfig(
                shot_type=ShotType.WS,
                environment=CHAOTIC_DORM,
                action="Wide jittery pan across Emma's room. Thousands of digital windows overlap in the air—PDFs, YouTube playlists, and research articles. Emma rubs her tired eyes, looking defeated by the stacks of books and open browser tabs.",
                narration=(
                    "In a world where information moves faster than we can think, we often find ourselves lost. "
                    "Emma is a brilliant student, but even she is drowning in a sea of millions of PDFs, endless playlists, "
                    "and a thousand open tabs that lead nowhere. She's looking for wisdom, but she only finds noise."
                ),
                # This will be ~15s, triggering recursive splitting (8s + 7s)
                duration_seconds=None
            ),

            # 2. The Discovery
            ShotConfig(
                shot_type=ShotType.CU,
                environment=CHAOTIC_DORM,
                action="Close-up on Emma's laptop screen. She opens ContextBytes. A warm golden pulse radiates from the center. The Keeper orb emerges from the UI, its light cleaning the digital clutter into organized spheres.",
                narration="Meet Emma. She didn't need more data; she needed a way to make sense of it. She found ContextBytes.",
                duration_seconds=None,
                continuity_required=True
            ),

            # 3. The AI Teacher
            ShotConfig(
                shot_type=ShotType.MS,
                environment=GITHUB_GARDEN,
                action="Shot in the Garden Atelier. The Keeper levitates, projecting a glowing teal 3D biology model. Emma watches, her face lighting up as she finally understands. The atmosphere is peaceful.",
                narration="Our agent, the ContextKeeper, doesn't just give answers. It guides you, explains the 'why', and organizes your path to mastery.",
                duration_seconds=None,
                continuity_required=True
            ),

            # 4. David's Professional Struggle
            ShotConfig(
                shot_type=ShotType.WS,
                environment=CORPORATE_MAZE,
                action="A high-angle shot of David in a sleek, cold tech office. He's dwarfed by skyscrapers of technical documentation and architectural specs. He looks stressed, trying to find clarity in the noise.",
                narration=(
                    "And then there’s David. A professional engineer lost in the giant tech machine, "
                    "drowning in documentation, architectural specs, and complex specs that seem to have no end. "
                    "In the corporate maze, context is the first thing that we lose."
                ),
                duration_seconds=None  # Split likely (8s + 4s)
            ),

            # 5. David's Clarity
            ShotConfig(
                shot_type=ShotType.WS,
                environment=CORPORATE_MAZE,
                action="The Keeper orb flies through David's office. Behind it, a beautiful glowing golden Knowledge Graph appears, physically connecting documents like a magical glowing architecture map.",
                narration="ContextBytes reveals the invisible threads between documents—transforming a mountain of text into a clear, magical map of how everything flows.",
                duration_seconds=None,
                continuity_required=True
            ),

            # 6. Final Harmony
            ShotConfig(
                shot_type=ShotType.WS,
                environment=GITHUB_GARDEN,
                action="Emma and David stand on a balcony overlooking the Cloud Stratosphere. They look confident and inspired. The Keeper orb flies toward the camera, merging into the final brand signature.",
                narration=(
                    "From the student's desk to the corporate boardroom, the path to mastery is now clear. "
                    "Deep simplicity. Modern intelligence. This is your Context, mastered. Welcome to ContextBytes."
                ),
                duration_seconds=None,
                continuity_required=True
            )
        ]
    )

    config = VideoConfig(
        persona=DEFAULT_PERSONA,
        style_dna=STYLE_DNA,
        cinematography=PREMIUM_CINE,
        output_dir="./contextbytes_production",
        aspect_ratio="16:9",
        negative_prompt="photorealistic, 3d render, CGI, grainy, distorted face, bad anatomy, low quality"
    )

    # Run the production
    result = await orchestrator.generate_production(
        scene=scene,
        base_config=config,
        output_filename="contextbytes_flagship_dynamic.mp4"
    )

    if result["success"]:
        print(
            f"✨ SUCCESS! Dynamic Flagship video saved to: {result['local_path']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(create_brand_video())
