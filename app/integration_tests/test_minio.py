"""Script to test MinIO/Storage component
"""
import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from common.configs import Config, OsVariable


MINIO_ENDPOINT = Config.os_get(OsVariable.MINIO_ENDPOINT.value)  # External port
ACCESS_KEY = Config.os_get(OsVariable.MINIO_ROOT_USER.value) or "admin"
SECRET_KEY = Config.os_get(OsVariable.MINIO_ROOT_PASSWORD.value) or "password"
BUCKET = "warehouse"


# Create S3 client
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=BotoConfig(signature_version='s3v4'),
    region_name='us-east-1'
)

print("Testing MinIO connection...")

# Test 1: List buckets
try:
    response = s3.list_buckets()
    print(f"Connected! Buckets: {[b['Name'] for b in response['Buckets']]}")
except ClientError as e:
    print(f"Connection failed: {e}")
    exit(1)

# Test 2: Check bucket exists
try:
    s3.head_bucket(Bucket=BUCKET)
    print(f"Bucket '{BUCKET}' exists")
except ClientError as e:
    print(f"Bucket check failed: {e}")
    exit(1)

# Test 3: Upload file
file_key = "test/kafka-connect-test.txt"
try:
    test_data = b"Hello from Kafka Connect test!"
    s3.put_object(Bucket=BUCKET, Key=file_key, Body=test_data)
    print("Upload successful")
except ClientError as e:
    print(f"Upload failed (403 = permission issue): {e}")
    exit(1)

# Test 4: Read file
try:
    obj = s3.get_object(Bucket=BUCKET, Key=file_key)
    data = obj['Body'].read()
    print(f"Read successful: {data.decode()}")
except ClientError as e:
    print(f"Read failed: {e}")
    exit(1)

# Test 5: Delete file
try:
    s3.delete_object(Bucket=BUCKET, Key="test/kafka-connect-test.txt")
    print("Delete successful")
except ClientError as e:
    print(f"Delete failed: {e}")

print("\nAll tests passed! MinIO is configured correctly.")
