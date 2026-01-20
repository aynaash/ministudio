# Ministudio Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "ministudio.api:app", "--host", "0.0.0.0", "--port", "8000"]
