import boto3
from fastapi import UploadFile, HTTPException
from app.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None
)

async def upload_file_to_s3(file: UploadFile, folder: str = "documents") -> str:
    file_path = f"{folder}/{file.filename}"
    try:
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            file_path,
            ExtraArgs={"ContentType": file.content_type}
        )
        file_url = f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
        return file_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Failed: {str(e)}")