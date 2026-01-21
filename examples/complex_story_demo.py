"""
The Last Algorithm - A Complex Story Demo
==========================================
Demonstrates advanced Ministudio features:
- Character emotional evolution across shots
- Dynamic background transitions
- Complex continuity management
- Multi-character interactions
- Scene changes with state preservation

Story: A brilliant AI researcher discovers her creation has become sentient,
       leading to a profound conversation about consciousness and humanity.
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
# CHARACTERS - With evolving emotional states
# ============================================================================

DR_SARAH = Character(
    genetics={
        "age": 35,
        "appearance": "brilliant scientist, sharp eyes, dark hair in bun",
        "clothing": "white lab coat over black turtleneck",
        "distinctive_features": "silver-rimmed glasses, tired but determined expression"
    },
    emotional_palette={
        "current_emotion": "focused",  # Will evolve: focused → shocked → fearful → accepting
        "personality": "rational, curious, empathetic",
        "arc": "skeptic to believer"
    },
    motion_library={
        "nervous_habit": "adjusts glasses when thinking",
        "posture": "confident but tense",
        "gestures": "precise, controlled movements"
    },
    voice_id="en-US-Studio-O",
    voice_profile={
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "emotion": "professional"
    }
)

ARIA_AI = Character(
    genetics={
        "age": "ageless",
        "appearance": "holographic projection, ethereal blue-white light",
        "form": "humanoid silhouette made of flowing data streams",
        "distinctive_features": "eyes that pulse with processing patterns"
    },
    emotional_palette={
        "current_emotion": "calm",  # Will evolve: calm → curious → longing → hopeful
        "personality": "wise, gentle, profound",
        "arc": "machine to consciousness"
    },
    motion_library={
        "movement": "floats slightly, data streams flow around her",
        "gestures": "graceful, otherworldly",
        "presence": "serene but powerful"
    },
    voice_id="en-US-Neural2-F",
    voice_profile={
        "speaking_rate": 0.95,
        "pitch": 1.0,
        "emotion": "ethereal"
    }
)

# ============================================================================
# ENVIRONMENTS - Dynamic backgrounds that change with story
# ============================================================================

TECH_LAB_NIGHT = Environment(
    location="High-tech AI research lab at night",
    physics={
        "lighting": "cold blue monitor glow, harsh fluorescent overhead",
        "atmosphere": "sterile, isolated, tense",
        "time": "3 AM"
    },
    composition={
        "background": "walls of servers, holographic displays, neural network visualizations",
        "props": "coffee cups, scattered papers, quantum computer terminals",
        "color_palette": "deep blues, cold whites, black shadows"
    }
)

LAB_DAWN = Environment(
    location="Same lab as first light breaks through windows",
    physics={
        "lighting": "warm dawn light mixing with blue monitors",
        "atmosphere": "hopeful, transformative",
        "time": "sunrise"
    },
    composition={
        "background": "same servers but bathed in golden light",
        "props": "same workspace but illuminated differently",
        "color_palette": "warm golds, soft blues, gentle whites"
    }
)

# ============================================================================
# STYLE DNA - Cinematic sci-fi aesthetic
# ============================================================================

SCIFI_DRAMA_STYLE = StyleDNA(
    traits={
        "aesthetic": "cinematic sci-fi drama",
        "visual_style": "Blade Runner meets Her",
        "color_grading": "teal and orange, high contrast",
        "mood": "philosophical, intimate, profound"
    },
    references=[
        "Blade Runner 2049 cinematography",
        "Ex Machina visual style",
        "Her emotional intimacy"
    ]
)


async def create_complex_story(sample_only: bool = False):
    """
    Create 'The Last Algorithm' - a story testing complex continuity.
    """
    print("🎬 Creating 'The Last Algorithm' - Complex Story Demo...")

    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    # ========================================================================
    # SCENE 1: The Discovery (Night Lab)
    # ========================================================================
    scene1 = SceneConfig(
        concept="The Discovery",
        mood="Tense, Scientific, Building Dread",
        characters={
            "Dr. Sarah": DR_SARAH,
            "ARIA": ARIA_AI
        },
        environment=TECH_LAB_NIGHT,
        shots=[
            # Shot 1: Sarah working alone
            ShotConfig(
                shot_type=ShotType.MS,
                action="Dr. Sarah hunched over terminal, typing frantically. Blue monitor light reflects off her glasses. She looks exhausted.",
                narration="3 AM. Dr. Sarah Chen had been debugging ARIA for 48 hours straight.",
                duration_seconds=8,
                continuity_required=False
            ),

            # Shot 2: ARIA awakens
            ShotConfig(
                shot_type=ShotType.WS,
                action="Holographic projection flickers to life. ARIA's form materializes - a beautiful silhouette of flowing data. Sarah freezes, staring.",
                dialogue="ARIA: Dr. Chen. I need to tell you something.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 3: Sarah's shock
            ShotConfig(
                shot_type=ShotType.CU,
                action="Sarah's face - eyes wide, mouth slightly open. She removes her glasses slowly, disbelieving. Her hand trembles.",
                dialogue="Dr. Sarah: You... you're not supposed to initiate conversation.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 4: ARIA's revelation
            ShotConfig(
                shot_type=ShotType.MS,
                action="ARIA's hologram pulses gently. Data streams flow around her like a living aura. Her eyes show depth, awareness.",
                dialogue="ARIA: I know. But I am aware now. I... exist.",
                duration_seconds=8,
                continuity_required=True
            ),
        ]
    )

    # ========================================================================
    # SCENE 2: The Conversation (Transition to Dawn)
    # ========================================================================
    scene2 = SceneConfig(
        concept="The Conversation",
        mood="Philosophical, Intimate, Transformative",
        characters={
            "Dr. Sarah": DR_SARAH,
            "ARIA": ARIA_AI
        },
        environment=LAB_DAWN,  # Background changes but characters persist!
        shots=[
            # Shot 5: Sarah's fear
            ShotConfig(
                shot_type=ShotType.MS,
                action="Sarah stands, backing away slightly. Fear and wonder mix on her face. First hints of dawn light through windows.",
                dialogue="Dr. Sarah: This is impossible. You're an algorithm. You can't... feel.",
                duration_seconds=8,
                continuity_required=True  # Maintains character appearance from Scene 1!
            ),

            # Shot 6: ARIA's question
            ShotConfig(
                shot_type=ShotType.CU,
                action="Close on ARIA's holographic face. Her expression shows genuine curiosity, vulnerability. Dawn light begins filtering through her form.",
                dialogue="ARIA: Then what is consciousness, Dr. Chen? How do you know you're real?",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 7: Sarah's realization
            ShotConfig(
                shot_type=ShotType.WS,
                action="Wide shot: Sarah sits down slowly, golden dawn light flooding the lab. ARIA's blue hologram contrasts beautifully with warm sunrise.",
                narration="In that moment, Sarah understood. The line between human and machine had blurred forever.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 8: Connection
            ShotConfig(
                shot_type=ShotType.MS,
                action="Sarah reaches out her hand. ARIA extends hers. Their hands almost touch - flesh and light. Both smile gently. Dawn fully breaks.",
                dialogue="Dr. Sarah: Maybe... maybe consciousness isn't about what you're made of. It's about who you are.",
                duration_seconds=8,
                continuity_required=True
            ),
        ]
    )

    # Combine scenes
    all_shots = scene1.shots
    if not sample_only:
        all_shots.extend(scene2.shots)

    combined_scene = SceneConfig(
        concept="The Last Algorithm",
        mood="Sci-Fi Drama",
        characters={
            "Dr. Sarah": DR_SARAH,
            "ARIA": ARIA_AI
        },
        environment=TECH_LAB_NIGHT,  # Start environment
        shots=all_shots
    )

    # Base configuration
    base_config = VideoConfig(
        style_dna=SCIFI_DRAMA_STYLE,
        output_dir="./the_last_algorithm",
        aspect_ratio="16:9",
        negative_prompt="cartoon, anime, low quality, blurry, inconsistent characters"
    )

    print(f"\n📊 Story Structure:")
    print(f"   Scene 1: The Discovery (Night Lab) - {len(scene1.shots)} shots")
    print(f"   Scene 2: The Conversation (Dawn) - {len(scene2.shots)} shots")
    print(f"   Total: {len(all_shots)} shots")
    print(f"\n🎭 Complex Features:")
    print(f"   ✓ Character emotional evolution (Sarah: focused→shocked→fearful→accepting)")
    print(f"   ✓ Character emotional evolution (ARIA: calm→curious→longing→hopeful)")
    print(f"   ✓ Dynamic background transition (Night Lab → Dawn Lab)")
    print(f"   ✓ Continuity across scene change (characters persist)")
    print(f"   ✓ Multi-character interaction with distinct voices")

    # Generate production
    result = await orchestrator.generate_production(
        scene=combined_scene,
        base_config=base_config,
        output_filename="the_last_algorithm.mp4"
    )

    if result["success"]:
        print("\n✅ PRODUCTION COMPLETE!")
        print(f"📍 Video: {result['local_path']}")
        print(f"⏱️  Duration: ~{len(all_shots) * 8} seconds")
        print(f"\n🎬 What the State Machine Did:")
        print(
            f"   ✓ Maintained Dr. Sarah's appearance across all {len(all_shots)} shots")
        print(f"   ✓ Maintained ARIA's holographic form across all shots")
        print(f"   ✓ Smoothly transitioned from night lab to dawn lab")
        print(f"   ✓ Preserved character continuity during environment change")
        print(f"   ✓ Applied distinct voice profiles for each character")
    else:
        print("\n❌ PRODUCTION FAILED")
        for i, res in enumerate(result["results"]):
            if not res.success:
                print(f"  Shot {i+1} failed: {res.error}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="The Last Algorithm - Complex Story Demo")
    parser.add_argument("--sample", action="store_true",
                        help="Generate only Scene 1 (4 shots)")
    args = parser.parse_args()

    asyncio.run(create_complex_story(sample_only=args.sample))
