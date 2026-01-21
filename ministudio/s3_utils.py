"""
S3 Utilities for Ministudio.
Handles uploading generated media to AWS S3.
"""

import os
import logging
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Uploader:
    def __init__(self, bucket_name: Optional[str] = None, region_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")

        if not self.bucket_name:
            logger.warning("S3_BUCKET_NAME not set. S3 uploads will fail.")

        try:
            self.s3_client = boto3.client('s3', region_name=self.region_name)
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None

    def upload_file(self, file_path: Path, object_name: Optional[str] = None, extra_args: Optional[dict] = None) -> Optional[str]:
        """
        Uploads a file to S3 and returns the public URL.
        """
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client or bucket name not available.")
            return None

        if object_name is None:
            object_name = file_path.name

        if extra_args is None:
            extra_args = {'ContentType': 'video/mp4'}

        try:
            logger.info(
                f"Uploading {file_path} to S3 bucket {self.bucket_name} as {object_name}...")
            self.s3_client.upload_file(
                str(file_path), self.bucket_name, object_name, ExtraArgs=extra_args)

            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{object_name}"
            logger.info(f"Successfully uploaded to: {url}")
            return url
        except ClientError as e:
            logger.error(f"S3 Upload Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return None
