"""
FastAPI server for Ministudio - Self-hostable AI video generation API.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core import Ministudio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ministudio API",
    description="Model-Agnostic AI Video Generation API",
    version="0.1.0"
)

# Default provider - can be configured
provider = Ministudio.create_provider("mock")
studio = Ministudio(provider=provider)


class GenerateRequest(BaseModel):
    concept: str
    action: str
    duration: int = 8
    provider: str = "mock"  # Allow switching providers


@app.post("/generate")
async def generate_video(request: GenerateRequest):
    """Generate a video based on concept and action"""
    try:
        # Allow provider switching if specified
        if request.provider != "mock":
            try:
                new_provider = Ministudio.create_provider(request.provider)
                global studio
                studio = Ministudio(provider=new_provider)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        result = await studio.generate_concept_video(
            concept=request.concept,
            action=request.action,
            duration=request.duration
        )

        response = {
            "success": result.success,
            "generation_time": result.generation_time,
            "provider": result.provider,
            "metadata": result.metadata
        }

        if result.video_path:
            response["video_path"] = str(result.video_path)
        if result.error:
            response["error"] = result.error

        return response

    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "Ministudio API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
