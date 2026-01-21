
import asyncio
import os
import json
from pathlib import Path
from ministudio import (
    Ministudio,
    ShotType,
    SceneConfig,
    ShotConfig,
    Character,
    Environment,
    VideoConfig
)


async def test_high_level_filmmaking():
    # 1. Initialize with mock provider (simulates generation)
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider, output_dir="./film_test_output")

    # 2. Define a film specification (JSON-compatible)
    film_spec = {
        "title": "Cosmic Adventure",
        "scenes": [
            {
                "concept": "Starship Bridge",
                "characters": {
                    "Captain": {"genetics": {"hair": "grey", "suit": "commander"}}
                },
                "environment": {"location": "cockpit of a starship"},
                "shots": [
                    {"shot_type": "WS", "action": "wide view of the bridge",
                        "duration_seconds": 2},
                    {"shot_type": "MS", "action": "Captain looking at the screen",
                        "duration_seconds": 2},
                    # Programmable Cut: Switch character mid-scene
                    {
                        "shot_type": "CU",
                        "action": "Close up of the Science Officer's eye",
                        "duration_seconds": 2,
                        "characters": {
                            "ScienceOfficer": {"genetics": {"hair": "blue", "suit": "science"}}
                        }
                    },
                    {"shot_type": "CU", "action": "Close up of the reactor button",
                        "duration_seconds": 2}
                ]
            }
        ]
    }

    # 3. Generate film with one call (under 15 lines of code logic)
    print("Starting film generation...")
    results = await studio.generate_film(film_spec)

    print(f"Generated {len(results)} shots.")
    for i, r in enumerate(results):
        print(f"Shot {i}: Success={r.success}, Path={r.video_path}")
        if r.video_path:
            # Check if frames were extracted
            frame_dir = r.video_path.parent / f"frames_{r.video_path.stem}"
            if frame_dir.exists():
                print(f"  Continuity frames extracted in: {frame_dir}")

if __name__ == "__main__":
    asyncio.run(test_high_level_filmmaking())
