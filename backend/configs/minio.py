from minio import Minio
import os

def init_minio():
    minio_url = os.getenv("MINIO_URL")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    print(minio_url, minio_access_key, minio_secret_key)
    minio_client = Minio(
        minio_url,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )
    return minio_client