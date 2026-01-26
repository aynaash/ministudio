"""
Vertex AI (Google Cloud) Adapter

Pre-configured adapter for GCP Vertex AI Veo 3.1.

Setup:
    1. Set VERTEX_AI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS
    2. Create provider:
        from ministudio.adapters import VertexAIAdapter
        provider = VertexAIAdapter.create(project_id="my-project")
    3. Use with orchestrator:
        orchestrator = VideoOrchestrator(provider)
"""

import os
from typing import Optional
from ..providers.vertex_ai import VertexAIProvider


class VertexAIAdapter:
    """Simplified Vertex AI provider setup"""
    
    RECOMMENDED_SETTINGS = {
        "model": "veo-3.1",
        "width": 512,
        "height": 512,
        "fps": 8,
        "quality_preset": "high",
    }
    
    @staticmethod
    def create(
        project_id: Optional[str] = None,
        location: str = "us-central1",
        **kwargs
    ) -> VertexAIProvider:
        """
        Create Vertex AI provider with minimal configuration.
        
        Args:
            project_id: GCP project ID (defaults to env var GCP_PROJECT_ID or VERTEX_AI_PROJECT_ID)
            location: GCP region (default: us-central1)
            **kwargs: Additional options to override defaults
        
        Returns:
            Configured VertexAIProvider instance
        
        Example:
            provider = VertexAIAdapter.create(project_id="my-project")
            result = await provider.generate_video(request)
        """
        if not project_id:
            project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("VERTEX_AI_PROJECT_ID")
            if not project_id:
                raise ValueError(
                    "project_id must be provided or set GCP_PROJECT_ID / VERTEX_AI_PROJECT_ID"
                )
        
        # Merge provided kwargs with defaults
        options = {**VertexAIAdapter.RECOMMENDED_SETTINGS, **kwargs}
        
        return VertexAIProvider(
            project_id=project_id,
            location=location,
            **options
        )
    
    @staticmethod
    def get_setup_instructions() -> str:
        """Return setup instructions for Vertex AI"""
        return """
=== Vertex AI Setup Instructions ===

1. Create a GCP project:
   https://console.cloud.google.com/projectcreate

2. Enable Vertex AI API:
   https://console.cloud.google.com/apis/library/aiplatform.googleapis.com

3. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant "Vertex AI User" role
   - Create a JSON key

4. Set up credentials (choose one):
   
   Option A: Environment variable (recommended for local dev)
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   
   Option B: Set in .env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   VERTEX_AI_PROJECT_ID=your-project-id

5. Usage:
   from ministudio.adapters import VertexAIAdapter
   provider = VertexAIAdapter.create(project_id="your-project-id")
"""


# Aliases for convenience
create_vertex_ai = VertexAIAdapter.create
