# backend/ingest/storage.py
import boto3
from backend.config import settings

def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

def upload_file(file_bytes: bytes, key: str, content_type: str = "application/pdf") -> str:
    _s3_client().put_object(
        Bucket=settings.r2_bucket_name,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return key

def download_file(key: str) -> bytes:
    response = _s3_client().get_object(Bucket=settings.r2_bucket_name, Key=key)
    return response["Body"].read()

def delete_file(key: str):
    _s3_client().delete_object(Bucket=settings.r2_bucket_name, Key=key)
