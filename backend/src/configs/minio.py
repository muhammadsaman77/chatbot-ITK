from minio import Minio
import os

def init_minio():
    minio_url = os.getenv("MINIO_URL")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")

    if not minio_url or not minio_access_key or not minio_secret_key:
        raise ValueError("MINIO_URL, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY environment variables must be set")

    minio_client = Minio(
        minio_url,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=minio_url.startswith("https")
    )
    return minio_client