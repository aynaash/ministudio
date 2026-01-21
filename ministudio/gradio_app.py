"""
Gradio web UI for Ministudio video generation.
Run with: python -m ministudio.gradio_app
"""

import gradio as gr
import asyncio
import logging
from . import Ministudio, VideoConfig

logger = logging.getLogger(__name__)


async def generate_video_ui(provider_name: str, concept: str, action: str, duration: int, style: str):
    """Generate video using Ministudio and update UI"""
    try:
        # 1. Create provider
        try:
            provider_obj = Ministudio.create_provider(provider_name)
        except Exception as e:
            return None, f"✗ Provider Error: {str(e)}"

        # 2. Create studio
        studio = Ministudio(provider=provider_obj)

        # 3. Create config based on UI inputs
        config = VideoConfig(
            duration_seconds=duration,
            style_name=style if style != "default" else "ghibli",
            mood="cinematic" if style == "cinematic" else "magical"
        )

        # 4. Generate video
        logger.info(f"UI Generation: {concept} - {action} ({provider_name})")
        result = await studio.generate_concept_video(
            concept=concept,
            action=action,
            config=config
        )

        if result.success and result.video_path:
            status = f"✓ Generated in {result.generation_time:.1f}s via {result.provider}"
            return str(result.video_path), status
        else:
            return None, f"✗ Generation failed: {result.error}"

    except Exception as e:
        logger.error(f"UI Error: {e}")
        return None, f"✗ System Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Ministudio - AI Video Generator") as demo:
    gr.Markdown("""
    # 🎬 Ministudio - AI Video Generator
    
    ### *The Kubernetes for AI Video*
    
    Generate consistent AI videos across multiple providers using a state-machine architecture.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            provider = gr.Dropdown(
                choices=["mock", "vertex-ai", "openai-sora"],
                value="mock",
                label="AI Provider",
                info="Select the backend AI engine"
            )

            style = gr.Dropdown(
                choices=["default", "ghibli", "cyberpunk",
                         "cinematic", "realistic"],
                value="ghibli",
                label="Visual Style",
                info="Visual aesthetic DNA"
            )

            duration = gr.Slider(
                minimum=1,
                maximum=60,
                value=8,
                step=1,
                label="Duration (seconds)",
            )

        with gr.Column(scale=2):
            concept = gr.Textbox(
                label="Concept",
                placeholder="e.g., Quantum Physics, Golden Orb, Ancient Library",
                lines=2
            )

            action = gr.Textbox(
                label="Scene Action",
                placeholder="e.g., the orb pulses with light as it discovers an old book",
                lines=3
            )

            generate_btn = gr.Button(
                "🎬 Generate Video", variant="primary", size="lg")

    with gr.Row():
        video_output = gr.Video(label="Generated Result", height=400)

    status_output = gr.Textbox(
        label="Status / Metadata",
        interactive=False,
        lines=2,
        placeholder="System logs will appear here..."
    )

    # Connect the function
    generate_btn.click(
        fn=generate_video_ui,
        inputs=[provider, concept, action, duration, style],
        outputs=[video_output, status_output]
    )

    gr.Markdown("""
    ### 🧠 Why Ministudio?
    - **Stateful**: Maintains character & environment consistency.
    - **Model-Agnostic**: Switch between Google Veo, Sora, and others instantly.
    - **Programmatic**: Code-as-Video configuration system.
    """)


if __name__ == "__main__":
    # Launch the web UI with Gradio 6.0 compatible parameters
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Soft(),
        share=False
    )
