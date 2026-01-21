"""
Gradio web UI for Ministudio video generation.
Run with: python -m ministudio.gradio_app
"""

import gradio as gr
import asyncio
from . import Ministudio


async def generate_video(provider: str, concept: str, action: str, duration: int, style: str):
    """Generate video using Ministudio"""
    try:
        # Create provider
        if provider == "vertex-ai":
            provider_obj = Ministudio.create_provider("vertex-ai", project_id="your-project")  # User needs to set
        elif provider == "openai-sora":
            provider_obj = Ministudio.create_provider("openai-sora", api_key="your-key")  # User needs to set
        else:
            provider_obj = Ministudio.create_provider("mock")

        # Create studio
        studio = Ministudio(provider=provider_obj)

        # Apply style if selected
        if style and style != "default":
            styles = {
                "ghibli": "ghibli",
                "cyberpunk": "cyberpunk",
                "cinematic": "cinematic",
                "realistic": "realistic"
            }
            if style in styles:
                from . import styles
                style_config = getattr(styles, styles[style] + '_style', None)
                if style_config:
                    studio.style_config = style_config

        # Generate video
        result = await studio.generate_concept_video(
            concept=concept,
            action=action,
            duration=duration
        )

        if result.success and result.video_path:
            status = f"✓ Video generated successfully in {result.generation_time:.1f}s"
            return str(result.video_path), status
        else:
            return None, f"✗ Generation failed: {result.error}"

    except Exception as e:
        return None, f"✗ Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Ministudio - AI Video Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎬 Ministudio - AI Video Generator

    Generate consistent AI videos across multiple providers.

    **Note:** For real providers, set your API keys in the code or environment variables.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            provider = gr.Dropdown(
                choices=["mock", "vertex-ai", "openai-sora"],
                value="mock",
                label="AI Provider",
                info="Select the AI model provider"
            )

            style = gr.Dropdown(
                choices=["default", "ghibli", "cyberpunk", "cinematic", "realistic"],
                value="ghibli",
                label="Visual Style",
                info="Choose the visual aesthetic"
            )

        with gr.Column(scale=2):
            concept = gr.Textbox(
                label="Concept",
                placeholder="e.g., Quantum Physics, Machine Learning, Climate Change",
                lines=2,
                info="The main topic or theme"
            )

            action = gr.Textbox(
                label="Action/Scene",
                placeholder="e.g., orb demonstrating wave functions, character exploring cave",
                lines=3,
                info="Describe what's happening in the video"
            )

            duration = gr.Slider(
                minimum=1,
                maximum=60,
                value=8,
                step=1,
                label="Duration (seconds)",
                info="Video length in seconds"
            )

    generate_btn = gr.Button("🎬 Generate Video", variant="primary", size="lg")

    with gr.Row():
        video_output = gr.Video(label="Generated Video", height=400)

    status_output = gr.Textbox(
        label="Status",
        interactive=False,
        lines=2,
        placeholder="Status messages will appear here..."
    )

    # Connect the function
    generate_btn.click(
        fn=generate_video,
        inputs=[provider, concept, action, duration, style],
        outputs=[video_output, status_output]
    )

    gr.Markdown("""
    ### About Ministudio
    - **Model-Agnostic**: Works with multiple AI providers
    - **State Management**: Maintains visual consistency
    - **Configurable**: Customize all generation parameters
    - **Extensible**: Easy to add new providers and styles

    ### Tips
    - Start with the "mock" provider to test without API keys
    - Use descriptive concepts and actions for better results
    - Experiment with different styles for varied aesthetics
    - Longer durations may take more time and cost more

    Made with ❤️ for the AI video generation community
    """)


if __name__ == "__main__":
    # Launch the web UI
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False  # Set to True for public sharing via Gradio
    )
