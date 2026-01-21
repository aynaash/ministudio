
import asyncio
import os
from ministudio import Ministudio, ShotType


async def produce_emma_spotlight_vertex():
    # Force Vertex AI Provider
    os.environ["MINISTUDIO_PROVIDER"] = "vertex-ai"

    studio = Ministudio(Ministudio.create_provider(
        "vertex-ai"), output_dir="./renders/emma_vertex_spotlight")

    emma = {
        "genetics": {"hair": "Short brown hair", "outfit": "blue sweater", "style": "Hand-painted cinematic aesthetic"},
        "voice_profile": {"gender": "female", "style": "warm", "accent": "British"}
    }

    spec = {
        "title": "Emma: The Joy of Context",
        "scenes": [
            {
                "concept": "The Overwhelmed Researcher",
                "characters": {"Emma": emma},
                "environment": {"location": "Messy digital desk, flickering blue screens"},
                "shots": [
                    {"shot_type": "CU", "narration": "Emma's digital world was a storm of fragments. Thousands of ideas, yet no threads to bind them.",
                        "action": "Emma looking overwhelmed at her desk, screens reflecting in her eyes", "duration_seconds": 10},
                    {
                        "shot_type": "MS",
                        "environment": {"location": "Warm desk with golden sunlight"},
                        "narration": "Until she discovered ContextBytes. A simple bridge between her research and her wisdom.",
                        "action": "Emma dragging a PDF into a golden glowing portal on her screen",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "WS",
                        "narration": "It automatically connected her textbook to her videos, revealing the invisible weave of her learning journey.",
                        "action": "Glowing teal threads connecting books to floating video windows",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "MCU",
                        "narration": "The search was over. Her digital workspace had transformed into a living garden of insight.",
                        "action": "Emma leaning back, smiling as golden knowledge vines grow around her",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "WS",
                        "narration": "From static data to dynamic mastery. This is Emma's learning, empowered.",
                        "action": "Wide of the room filled with floating knowledge nodes",
                        "duration_seconds": 10
                    },
                    {
                        "shot_type": "CU",
                        "narration": "This is your Context, mastered. Welcome to ContextBytes.",
                        "action": "Emma smiling at the camera, warm sunset lighting",
                        "duration_seconds": 10
                    }
                ]
            }
        ]
    }

    print("🚀 PRODUCING (VERTEX AI): Emma Spotlight (Narration-Driven)")
    await studio.generate_film(spec)

if __name__ == "__main__":
    asyncio.run(produce_emma_spotlight_vertex())
