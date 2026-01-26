"""
Audio Agent Examples
====================
Examples of using the Audio Agent to create videos from voice descriptions.
"""

import asyncio
import os


# Example 1: Process an audio file
def example_audio_file():
    """Convert an audio file to a video prompt."""
    from ministudio.audio_agent import audio_to_prompt
    
    # Record yourself saying:
    # "I want a cinematic shot of a spaceship flying through an asteroid field,
    #  with dramatic lighting and slow motion explosions"
    
    prompt = audio_to_prompt("my_description.wav")
    
    print(f"Style: {prompt.style}")      # "cinematic"
    print(f"Duration: {prompt.duration}")  # extracted or default
    print(f"Description: {prompt.description}")
    
    return prompt


# Example 2: Text input (for testing)
def example_text_input():
    """Use text directly (useful for testing without audio)."""
    from ministudio.audio_agent import text_to_prompt
    
    prompt = text_to_prompt(
        "Make me a 15 second cyberpunk video of a hacker in a neon-lit room, "
        "with rain on the windows and holographic displays floating around"
    )
    
    print(f"Style: {prompt.style}")        # "cyberpunk"
    print(f"Duration: {prompt.duration}")   # 15
    print(f"Mood: {prompt.mood}")          # extracted mood
    print(f"Camera: {prompt.camera_movements}")
    
    return prompt


# Example 3: Full pipeline - audio to video
async def example_full_pipeline():
    """Complete pipeline from audio to generated video."""
    from ministudio.audio_agent import AudioAgent
    
    agent = AudioAgent()
    
    # Process audio
    prompt = agent.process_audio("describe_video.wav")
    
    # Review what was understood
    print("Understood your request:")
    print(f"  {prompt.description}")
    print(f"  Style: {prompt.style}, Duration: {prompt.duration}s")
    
    # Generate video
    video_path = await agent.generate_video(prompt)
    print(f"Video saved to: {video_path}")
    
    return video_path


# Example 4: Interactive microphone session
def example_microphone():
    """Record from microphone and generate."""
    from ministudio.audio_agent import AudioAgent
    
    agent = AudioAgent()
    
    # This will record for 10 seconds
    prompt = agent.listen_and_generate(duration=10)
    
    print(f"You described: {prompt.original_transcript}")
    print(f"Compiled to: {prompt.description}")
    
    return prompt


# Example 5: Save and load prompts
def example_save_load():
    """Save prompts to JSON for later use."""
    from ministudio.audio_agent import AudioAgent, text_to_prompt
    
    agent = AudioAgent()
    
    # Create prompt
    prompt = text_to_prompt(
        "A peaceful nature scene with a waterfall in a forest, "
        "birds flying, 20 seconds long, calm and serene"
    )
    
    # Save for later
    agent.save_prompt(prompt, "my_nature_video.json")
    
    # Load and use later
    loaded_prompt = agent.load_prompt("my_nature_video.json")
    print(f"Loaded: {loaded_prompt.style}, {loaded_prompt.duration}s")
    
    return loaded_prompt


# Example 6: Use with different transcription providers
def example_providers():
    """Use different transcription providers."""
    from ministudio.audio_agent import AudioAgent, TranscriptionProvider
    
    # Local Whisper (free, requires model download)
    agent_local = AudioAgent(
        transcription_provider=TranscriptionProvider.WHISPER_LOCAL
    )
    
    # OpenAI Whisper API (paid, better accuracy)
    agent_api = AudioAgent(
        transcription_provider=TranscriptionProvider.WHISPER_API
    )
    
    # Google Cloud Speech (paid, good for noisy audio)
    agent_google = AudioAgent(
        transcription_provider=TranscriptionProvider.GOOGLE_SPEECH
    )
    
    # Deepgram (paid, fast and accurate)
    agent_deepgram = AudioAgent(
        transcription_provider=TranscriptionProvider.DEEPGRAM
    )
    
    # Use whichever you have configured
    return agent_local


# Example 7: Extract specific components
def example_extract_components():
    """Show how prompt components are extracted."""
    from ministudio.audio_agent import text_to_prompt
    
    # Complex description with many components
    prompt = text_to_prompt(
        "Create a 30 second horror video. "
        "Start with a dark forest at night, then cut to a mysterious figure. "
        "Use slow motion and dramatic zoom effects. "
        "The mood should be tense and scary. "
        "There's a character named Sarah who is running through the trees."
    )
    
    print("Extracted components:")
    print(f"  Style: {prompt.style}")           # "horror"
    print(f"  Duration: {prompt.duration}s")     # 30
    print(f"  Mood: {prompt.mood}")              # "tense" or similar
    print(f"  Camera: {prompt.camera_movements}")  # ["slow motion", "zoom"]
    print(f"  Shots: {len(prompt.shots)}")       # Multiple shots detected
    print(f"  Characters: {prompt.characters}")  # [{"name": "Sarah", ...}]
    
    for i, shot in enumerate(prompt.shots, 1):
        print(f"  Shot {i}: {shot['description'][:40]}...")
    
    return prompt


# Example 8: Interactive session
def example_interactive():
    """Run the full interactive session."""
    from ministudio.audio_agent import interactive_audio_session
    
    # This launches the interactive menu
    interactive_audio_session()


# Run examples
if __name__ == "__main__":
    print("Audio Agent Examples")
    print("=" * 50)
    
    # Run text example (doesn't require audio file)
    print("\n📝 Example: Text to Prompt")
    prompt = example_text_input()
    print(f"   Result: {prompt.style} style, {prompt.duration}s")
    
    print("\n🔍 Example: Component Extraction")
    prompt = example_extract_components()
    
    print("\n" + "=" * 50)
    print("To run interactive mode: python -m ministudio.audio_agent")
    print("Or: from ministudio.audio_agent import interactive_audio_session")
