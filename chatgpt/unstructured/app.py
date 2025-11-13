import os
import uuid
from datetime import datetime

import boto3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from unstructured.partition.auto import partition

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localstack:4566")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "documents")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

app = FastAPI(title="Unstructured Document Processor")


def ensure_bucket():
    existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if S3_BUCKET_NAME not in existing:
        s3.create_bucket(Bucket=S3_BUCKET_NAME)


ensure_bucket()


@app.post("/upload")
async def upload(request: Request):
    filename = request.headers.get("X-Filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Missing X-Filename header")

    raw_bytes = await request.body()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    tmp_path = f"/tmp/{uuid.uuid4()}_{filename}"
    with open(tmp_path, "wb") as f:
        f.write(raw_bytes)

    try:
        elements = partition(filename=tmp_path)
        text_content = "\n".join(
            [el.text for el in elements if hasattr(el, "text") and el.text]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing document: {e}") from e

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base_key = f"uploads/{timestamp}_{uuid.uuid4()}"

    original_key = f"{base_key}/{filename}"
    text_key = f"{base_key}/{filename}.txt"

    content_type = request.headers.get("Content-Type", "application/octet-stream")

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=original_key,
        Body=raw_bytes,
        ContentType=content_type,
    )

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=text_key,
        Body=text_content.encode("utf-8"),
        ContentType="text/plain",
    )

    return JSONResponse({"status": "ok", "key": base_key, "text_key": text_key})
