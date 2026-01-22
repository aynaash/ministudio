"""
Quantum Mechanics TikTok Demo
==============================
A 1-minute educational video with consistent characters and background.
Demonstrates Ministudio's state machine for continuity across shots.
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
# CHARACTER DEFINITIONS - These persist across ALL shots
# ============================================================================

GRANDFATHER = Character(
    genetics={
        "age": 70,
        "appearance": "elderly man with white beard and glasses",
        "clothing": "brown cardigan and khaki pants",
        "expression": "wise and patient"
    },
    emotional_palette={
        "current_emotion": "enthusiastic",
        "teaching_mode": True
    },
    motion_library={
        "gestures": "uses hands to explain concepts",
        "posture": "sitting comfortably in armchair"
    },
    voice_id="en-US-Neural2-D",  # Deep, warm voice
    voice_profile={
        "speaking_rate": 0.9,  # Slightly slower for clarity
        "pitch": -2.0  # Lower pitch
    }
)

GRANDDAUGHTER = Character(
    genetics={
        "age": 10,
        "appearance": "young girl with curious eyes and ponytail",
        "clothing": "colorful t-shirt and jeans",
        "expression": "curious and engaged"
    },
    emotional_palette={
        "current_emotion": "curious",
        "learning_mode": True
    },
    motion_library={
        "gestures": "leans forward when interested",
        "posture": "sitting cross-legged on floor"
    },
    voice_id="en-US-Neural2-F",  # Young, bright voice
    voice_profile={
        "speaking_rate": 1.1,  # Slightly faster
        "pitch": 2.0  # Higher pitch
    }
)

# ============================================================================
# ENVIRONMENT - Consistent background across all shots
# ============================================================================

COZY_STUDY = Environment(
    location="Warm, cozy study with bookshelves and soft lighting",
    physics={
        "lighting": "golden hour sunlight through window",
        "atmosphere": "peaceful and intimate",
        "time_of_day": "afternoon"
    },
    composition={
        "background": "wooden bookshelves filled with science books",
        "props": "armchair, floor cushion, quantum physics poster on wall",
        "color_palette": "warm browns, soft yellows, deep reds"
    }
)

# ============================================================================
# STYLE DNA - Visual consistency
# ============================================================================

EDUCATIONAL_STYLE = StyleDNA(
    traits={
        "aesthetic": "warm and inviting",
        "animation_style": "semi-realistic with slight cartoon charm",
        "color_grading": "warm tones, high saturation",
        "visual_mood": "educational but fun"
    },
    references=[
        "educational YouTube videos",
        "Pixar-style character design",
        "cozy interior photography"
    ]
)


async def create_quantum_tiktok():
    """
    Create a 1-minute TikTok explaining quantum mechanics.
    The state machine ensures characters and background stay consistent!
    """
    print("Creating Quantum Mechanics TikTok...")

    # Initialize provider and orchestrator
    provider = VertexAIProvider()
    orchestrator = VideoOrchestrator(provider)

    # Define the complete scene with multiple shots
    # Each shot maintains continuity through the state machine
    scene = SceneConfig(
        concept="Quantum Mechanics Explained",
        mood="Educational, Warm, Engaging",
        characters={
            "Grandfather": GRANDFATHER,
            "Granddaughter": GRANDDAUGHTER
        },
        environment=COZY_STUDY,
        shots=[
            # Shot 1: Introduction (8 seconds)
            ShotConfig(
                shot_type=ShotType.MS,  # Medium shot of both characters
                action="Grandfather sitting in armchair, granddaughter on floor looking up at him with curious expression. He smiles warmly.",
                dialogue="Granddaughter: Grandpa, what is quantum mechanics?",
                duration_seconds=8,
                continuity_required=False  # First shot, no previous frames
            ),

            # Shot 2: Explanation begins (8 seconds)
            ShotConfig(
                shot_type=ShotType.CU,  # Close-up on grandfather
                action="Grandfather's face lights up with excitement. He leans forward slightly, gesturing with his hands.",
                dialogue="Grandfather: Ah! It's the science of the very, very small - smaller than atoms!",
                duration_seconds=8,
                continuity_required=True  # Use last frames from Shot 1
            ),

            # Shot 3: Visual metaphor (8 seconds)
            ShotConfig(
                shot_type=ShotType.WS,  # Wide shot showing both
                action="Grandfather holds up his hands, creating an imaginary tiny space between them. Granddaughter's eyes widen with wonder.",
                narration="Imagine a world where particles can be in two places at once.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 4: The mystery (8 seconds)
            ShotConfig(
                shot_type=ShotType.MS,  # Back to medium shot
                action="Granddaughter tilts her head, thinking. Grandfather watches her with a knowing smile.",
                dialogue="Granddaughter: Two places at once? That's impossible!",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 5: The revelation (8 seconds)
            ShotConfig(
                shot_type=ShotType.CU,  # Close-up on grandfather
                action="Grandfather's eyes twinkle. He raises one finger in a teaching gesture.",
                dialogue="Grandfather: That's what makes it quantum! It breaks all the rules we know.",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 6: Understanding dawns (8 seconds)
            ShotConfig(
                shot_type=ShotType.MS,  # Medium shot of both
                action="Granddaughter's face shows realization. She smiles and nods. Grandfather pats her shoulder proudly.",
                dialogue="Granddaughter: Wow! Science is so cool, Grandpa!",
                duration_seconds=8,
                continuity_required=True
            ),

            # Shot 7: Closing (8 seconds)
            ShotConfig(
                shot_type=ShotType.WS,  # Wide shot for ending
                action="Both characters laugh together. Warm sunlight fills the study. Camera slowly pulls back.",
                narration="And that's quantum mechanics - where the impossible becomes possible.",
                duration_seconds=8,
                continuity_required=True
            )
        ]
    )

    # Base configuration with style
    base_config = VideoConfig(
        style_dna=EDUCATIONAL_STYLE,
        output_dir="./quantum_tiktok",
        aspect_ratio="9:16",  # TikTok vertical format
        negative_prompt="blurry, inconsistent characters, changing backgrounds, poor lighting"
    )

    # Generate the full production
    # The state machine will:
    # 1. Track Grandfather and Granddaughter across all shots
    # 2. Maintain the COZY_STUDY environment
    # 3. Use last frames from each shot for continuity
    # 4. Apply consistent style DNA
    result = await orchestrator.generate_production(
        scene=scene,
        base_config=base_config,
        output_filename="quantum_mechanics_explained.mp4"
    )

    if result["success"]:
        print("\nTIKTOK CREATED!")
        print(f"Video: {result['local_path']}")
        print(f" Duration: ~56 seconds (7 shots × 8 seconds)")
        print(f"Characters: Grandfather & Granddaughter (consistent across all shots)")
        print(f"Environment: Cozy Study (maintained throughout)")
    else:
        print("\nPRODUCTION FAILED")
        for i, res in enumerate(result["results"]):
            if not res.success:
                print(f"  Shot {i+1} failed: {res.error}")


if __name__ == "__main__":
    asyncio.run(create_quantum_tiktok())
