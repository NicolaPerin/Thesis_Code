from minio import Minio

minio_client = Minio(
    "localhost:9000",
    access_key="PAAXbVRzuAoPxeBygtmj",
    secret_key="XqnxMxI2EqJFo5RbPvcAnvbdQ1tRg3jRfMZz9OSb",
    secure=False,
)

def upload_file_to_minio(bucket_name, file_name, file_data):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    minio_client.put_object(bucket_name, file_name, file_data, length=-1, part_size=10*1024*1024)
