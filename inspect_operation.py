"""
Deep diagnostic to inspect the full operation object
"""
import asyncio
import logging
import json

logging.basicConfig(level=logging.DEBUG)


async def inspect_operation():
    from ministudio.providers.vertex_ai import VertexAIProvider
    from ministudio.interfaces import VideoGenerationRequest
    from google.genai import types
    from google import genai

    print("Initializing provider...")
    provider = VertexAIProvider()

    # Initialize client
    client = genai.Client(
        project=provider.project_id,
        location=provider.location,
        vertexai=True,
        credentials=provider.credentials
    )

    print("Starting video generation...")
    source = types.GenerateVideosSource(
        prompt="A golden orb floating, Ghibli style")
    config = types.GenerateVideosConfig(
        aspect_ratio="16:9", duration_seconds=5)

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        source=source,
        config=config
    )

    print(f"\nInitial operation state:")
    print(f"  Name: {operation.name}")
    print(f"  Done: {operation.done}")

    # Poll once
    await asyncio.sleep(5)
    operation = client.operations.get(operation)

    print(f"\nAfter 5s:")
    print(f"  Done: {operation.done}")
    print(f"  Result: {operation.result}")
    print(f"  Response: {operation.response}")
    print(
        f"  Error: {operation.error if hasattr(operation, 'error') else 'N/A'}")

    # Check metadata
    if hasattr(operation, 'metadata') and operation.metadata:
        print(f"\nMetadata type: {type(operation.metadata)}")
        print(f"Metadata: {operation.metadata}")

        # Try to convert to dict
        try:
            if hasattr(operation.metadata, 'to_dict'):
                meta_dict = operation.metadata.to_dict()
            elif hasattr(operation.metadata, 'model_dump'):
                meta_dict = operation.metadata.model_dump()
            else:
                meta_dict = dict(operation.metadata) if hasattr(
                    operation.metadata, '__iter__') else str(operation.metadata)

            print(f"\nMetadata as dict:")
            print(json.dumps(meta_dict, indent=2, default=str))
        except Exception as e:
            print(f"Could not convert metadata: {e}")

    # Try to get the raw API response
    if hasattr(operation, '_raw_page'):
        print(f"\nRaw page: {operation._raw_page}")

    print(f"\nAll operation attributes:")
    for attr in dir(operation):
        if not attr.startswith('_'):
            try:
                val = getattr(operation, attr)
                if not callable(val):
                    print(
                        f"  {attr}: {type(val)} = {val if len(str(val)) < 100 else str(val)[:100] + '...'}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(inspect_operation())
