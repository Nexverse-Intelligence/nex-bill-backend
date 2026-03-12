# Standard library

# Third-party
import boto3

# Local
from app.config import settings


class S3Client:
    """
    Wraps boto3 S3 operations for file storage.
    Compatible with AWS S3 and MinIO.
    """

    def __init__(self) -> None:
        kwargs: dict = {
            "region_name": settings.AWS_REGION,
            "aws_access_key_id": (settings.AWS_ACCESS_KEY_ID),
            "aws_secret_access_key": (settings.AWS_SECRET_ACCESS_KEY),
        }
        if settings.S3_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
        self._client = boto3.client("s3", **kwargs)
        self._bucket = settings.S3_BUCKET

    def upload(
        self,
        key: str,
        data: bytes,
        content_type: str,
    ) -> str:
        """
        Upload bytes to S3 and return the object URL.

        Args:
            key: S3 object key (path).
            data: Raw file bytes to upload.
            content_type: MIME type of the file.

        Returns:
            Public or pre-signed URL for the object.
        """
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return self.get_presigned_url(key)

    def get_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate a pre-signed download URL.

        Args:
            key: S3 object key.
            expires_in: URL lifetime in seconds.

        Returns:
            Pre-signed URL string.
        """
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )

    def delete(self, key: str) -> None:
        """
        Delete an object from S3.

        Args:
            key: S3 object key to delete.
        """
        self._client.delete_object(
            Bucket=self._bucket,
            Key=key,
        )
