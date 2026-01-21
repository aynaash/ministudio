
import asyncio
import os
from ministudio import Ministudio, ShotType


async def produce_david_spotlight_vertex():
    # Force Vertex AI Provider
    os.environ["MINISTUDIO_PROVIDER"] = "vertex-ai"

    studio = Ministudio(Ministudio.create_provider(
        "vertex-ai"), output_dir="./renders/david_vertex_spotlight")

    david = {
        "genetics": {"hair": "Short dark hair", "accessories": "glasses", "outfit": "green scarf"},
        "voice_profile": {"gender": "male", "style": "professional, calm", "accent": "American"}
    }

    spec = {
        "title": "David: Precision Training",
        "scenes": [
            {
                "concept": "The New Hire",
                "characters": {"David": david},
                "environment": {"location": "Corporate office, modern and slightly sterile"},
                "shots": [
                    {"shot_type": "MS", "narration": "For David, corporate compliance was a mountain of text. A mandatory hurdle in his busy day.",
                        "action": "David looking at a massive 100-page document on screen", "duration_seconds": 10},
                    {
                        "shot_type": "CU",
                        "narration": "But with ContextBytes, he didn't just read. He understood. Instantly.",
                        "action": "The Golden ContextKeeper Orb scanning the document",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "MS",
                        "narration": "The system mapped the policy directly to his real-world tasks, highlighting what mattered most.",
                        "action": "Interactive code snippets appearing next to policy text",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "MCU",
                        "narration": "Automated assessments ensured mastery, turning passive training into active competency.",
                        "action": "David answering quiz questions efficiently",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "WS",
                        "narration": "From a new hire to a trusted professional. David reached certification in record time.",
                        "action": "David holding a digital certificate that pulses with gold light",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "CU",
                        "narration": "Modern intelligence for the modern professional. ContextBytes.",
                        "action": "David walking out of the office into a bright, empowering sun",
                        "duration_seconds": 10
                    }
                ]
            }
        ]
    }

    print("🚀 PRODUCING (VERTEX AI): David Spotlight (Narration-Driven)")
    await studio.generate_film(spec)

if __name__ == "__main__":
    asyncio.run(produce_david_spotlight_vertex())
