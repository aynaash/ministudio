"""
S3 Utilities
============
AWS S3 upload utilities for video assets.

This module provides optional S3 upload functionality.
If boto3 is not installed, it gracefully falls back to local storage.
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import boto3
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.info("boto3 not installed - S3 uploads disabled")


class S3Uploader:
    """
    Simple S3 uploader for video assets.
    
    Falls back gracefully if AWS credentials not configured.
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        prefix: str = "videos/"
    ):
        """
        Initialize S3 uploader.
        
        Args:
            bucket_name: S3 bucket name (or from AWS_S3_BUCKET env)
            region: AWS region (or from AWS_REGION env)
            prefix: Key prefix for uploads
        """
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.prefix = prefix
        self._client = None
        self._available = False
        
        # Check if we can use S3
        if HAS_BOTO3 and self.bucket_name:
            try:
                self._client = boto3.client('s3', region_name=self.region)
                self._available = True
                logger.info(f"S3 uploader initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if S3 uploads are available."""
        return self._available
    
    def upload_file(
        self,
        local_path: str,
        key: Optional[str] = None,
        content_type: str = "video/mp4"
    ) -> Optional[str]:
        """
        Upload a file to S3.
        
        Args:
            local_path: Path to local file
            key: S3 key (defaults to prefix + filename)
            content_type: MIME type of the file
        
        Returns:
            S3 URI if successful, None otherwise
        """
        if not self._available:
            logger.debug("S3 not available, skipping upload")
            return None
        
        # Verify file exists
        if not os.path.exists(local_path):
            logger.error(f"File not found: {local_path}")
            return None
        
        # Generate key if not provided
        if not key:
            filename = os.path.basename(local_path)
            key = f"{self.prefix}{filename}"
        
        try:
            self._client.upload_file(
                local_path,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': content_type}
            )
            s3_uri = f"s3://{self.bucket_name}/{key}"
            logger.info(f"Uploaded to S3: {s3_uri}")
            return s3_uri
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return None
    
    def upload_video(self, local_path: str, key: Optional[str] = None) -> Optional[str]:
        """Upload a video file to S3."""
        return self.upload_file(local_path, key, content_type="video/mp4")
    
    def upload_audio(self, local_path: str, key: Optional[str] = None) -> Optional[str]:
        """Upload an audio file to S3."""
        ext = os.path.splitext(local_path)[1].lower()
        content_type = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".aac": "audio/aac"
        }.get(ext, "audio/mpeg")
        return self.upload_file(local_path, key, content_type=content_type)
    
    def get_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a presigned URL for an S3 object.
        
        Args:
            key: S3 key
            expires_in: URL expiration time in seconds
        
        Returns:
            Presigned URL if successful, None otherwise
        """
        if not self._available:
            return None
        
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            key: S3 key to delete
        
        Returns:
            True if successful
        """
        if not self._available:
            return False
        
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted from S3: s3://{self.bucket_name}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False


# Convenience function
def upload_to_s3(local_path: str, bucket: Optional[str] = None) -> Optional[str]:
    """
    Quick upload to S3.
    
    Args:
        local_path: Path to file
        bucket: S3 bucket (optional, uses env var)
    
    Returns:
        S3 URI or None
    """
    uploader = S3Uploader(bucket_name=bucket)
    return uploader.upload_file(local_path)
