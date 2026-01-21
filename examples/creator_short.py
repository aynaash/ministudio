
import asyncio
from ministudio import Ministudio, ShotType


async def generate_creator_short():
    # 1. Initialize Ministudio (Mocking the AI for speed)
    studio = Ministudio(Ministudio.create_provider(
        "mock"), output_dir="./creator_output")

    # 2. Define a "Short Story" with dialogue and background cuts
    # This is < 15 lines of core logic
    short_story = {
        "title": "The Secret Ransom",
        "scenes": [
            {
                "concept": "Dark Alleyway",
                "conflict_matrix": {"Protagonist,Villain": "intense conflict"},
                "characters": {
                    "Protagonist": {"genetics": {"hair": "black", "jacket": "brown"}, "voice_id": "v1"},
                    "Villain": {"genetics": {"mask": "skull", "jacket": "black"}, "voice_id": "v2"}
                },
                "environment": {"location": "neon-lit dark alleyway, rain"},
                "shots": [
                    {"shot_type": "WS", "action": "wide view of the alleyway, rain falling",
                        "duration_seconds": 3},
                    {"shot_type": "CU", "dialogue": "Villain: Where is the package?",
                        "action": "Villain pointing a laser at the Protagonist", "duration_seconds": 2},
                    {"shot_type": "CU", "dialogue": "Protagonist: I don't have it here.",
                        "action": "Protagonist looking nervous", "duration_seconds": 2},

                    # Cut to different background while same characters are in conflict
                    {
                        "shot_type": "WS",
                        "action": "Car headlights flashing, illuminating the warehouse",
                        "environment": {"location": "abandoned warehouse interior"},
                        "dialogue": "Villain: Lies. We go to the warehouse.",
                        "duration_seconds": 4
                    }
                ]
            }
        ]
    }

    # 3. Produce the film
    print("Producing Creator Short: The Secret Ransom...")
    results = await studio.generate_film(short_story)

    print(f"Produced {len(results)} shots with synchronized dialogue audio.")

if __name__ == "__main__":
    import traceback
    try:
        asyncio.run(generate_creator_short())
    except Exception:
        traceback.print_exc()
