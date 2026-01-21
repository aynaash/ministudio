
import asyncio
from ministudio import Ministudio, ShotType


async def generate_documentary():
    # 1. Initialize Ministudio
    studio = Ministudio(Ministudio.create_provider(
        "mock"), output_dir="./doc_output")

    # 2. Nature Documentary Spec
    doc_spec = {
        "title": "The Infinite Forest",
        "scenes": [
            {
                "concept": "Ancient Pine Forest",
                "characters": {
                    "Explorer": {
                        "genetics": {"hair": "blonde", "outfit": "hiking gear"},
                        "voice_profile": {
                            "gender": "female",
                            "style": "energetic",
                            "accent": "British"
                        }
                    }
                },
                "environment": {"location": "dense misty forest with giant pines"},
                "shots": [
                    {
                        "shot_type": "WS",
                        "narration": "Deep within the Infinite Forest, secrets lie buried beneath the moss.",
                        "action": "Drone flyover of a misty forest canopy",
                        "duration_seconds": 4
                    },
                    {
                        "shot_type": "MS",
                        "action": "Explorer walking through tall grass",
                        "dialogue": "Explorer: Look at these tracks. Something huge was here.",
                        "duration_seconds": 3
                    },
                    {
                        "shot_type": "ECU",
                        "narration": "Every footprint tells a story of survival.",
                        "action": "Extreme close up of a massive paw print in mud",
                        "duration_seconds": 2
                    }
                ]
            }
        ]
    }

    # 3. Produce the film
    print("Producing Nature Documentary: The Infinite Forest...")
    results = await studio.generate_film(doc_spec)

    print(f"Produced Documentary with Narrator and Explorer (Husky/Energetic voices).")

if __name__ == "__main__":
    asyncio.run(generate_documentary())
