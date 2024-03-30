from minio import Minio
from minio.error import S3Error


class MinioClient:
    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(endpoint,
                            access_key=access_key,
                            secret_key=secret_key,
                            secure=False)  # Change to True if using HTTPS

    def list_buckets(self):
        try:
            buckets = self.client.list_buckets()
            for bucket in buckets:
                print(bucket.name)
        except S3Error as e:
            print(e)

    def create_bucket(self, bucket_name):
        try:
            self.client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        except S3Error as e:
            print(e)

    def list_objects(self, bucket_name):
        return self.client.list_objects(bucket_name, include_version=True, include_user_meta=True)

    # def upload_file(self, bucket_name, file_path, object_name=None):
    #     try:
    #         if not object_name:
    #             object_name = file_path.split('/')[-1]  # Use the file name as object name if not provided
    #         self.client.fput_object(bucket_name, object_name, file_path)
    #         print(f"File '{object_name}' uploaded successfully.")
    #     except S3Error as e:
    #         print(e)
    @staticmethod
    def get_client():
        return MinioClient(endpoint="localhost:9000",
                           access_key="minioadmin",
                           secret_key="minioadmin")

    @classmethod
    def first_run(cls):
        minio_client = cls.get_client()
        minio_client.list_buckets()
        minio_client.create_bucket("music-bucket")
        # minio_client.upload_file("music-bucket", "path/to/local/file.txt")
