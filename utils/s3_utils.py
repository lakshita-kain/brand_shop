import boto3
from io import BytesIO
from PIL import Image
from config.setting import AWS_ACCESS_KEY, AWS_SECRET_KEY

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

def list_images(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    return [
        obj["Key"]
        for page in pages
        for obj in page.get("Contents", [])
        if obj["Key"].lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def load_image(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return Image.open(BytesIO(obj["Body"].read())).convert("RGB")
