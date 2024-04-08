from datetime import datetime
from io import BytesIO

from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
from minio.versioningconfig import VersioningConfig

from settings import MINIO_BUCKET_NAME, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_PORT
from minio.lifecycleconfig import Expiration, Rule, LifecycleConfig
from minio.commonconfig import Filter

from utils import is_mp3


class MinioClient:
    _instance = None

    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        print(self.endpoint)
        print(self.access_key)
        print(self.secret_key)
        print(self.secure)
        self.client = Minio(endpoint,
                            access_key=access_key,
                            secret_key=secret_key,
                            secure=secure)

    @classmethod
    def get_instance(cls, endpoint=f"{MINIO_ENDPOINT}:{MINIO_PORT}", access_key=MINIO_ACCESS_KEY,
                     secret_key=MINIO_SECRET_KEY):
        if cls._instance is None:
            cls._instance = cls(endpoint, access_key, secret_key)
        return cls._instance

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

    def set_rules(self):
        filter_prefix = Filter(prefix="")
        expiration = Expiration(days=1)
        rule = Rule(status='Enabled', expiration=expiration, rule_filter=filter_prefix)
        config = LifecycleConfig([rule])
        self.client.set_bucket_lifecycle(MINIO_BUCKET_NAME, config)

    def initialize(self):
        self.list_buckets()
        self.create_bucket(MINIO_BUCKET_NAME)
        self.set_rules()

    async def save_file_to_minio(self, file: UploadFile):
        bucket_name = MINIO_BUCKET_NAME
        buffer = BytesIO()
        while True:
            chunk = await file.read(1024)  # Read 1 KB at a time
            if not chunk:
                break
            buffer.write(chunk)

        if not is_mp3(buffer):
            raise HTTPException(status_code=400, detail="Uploaded file is not an MP3")

        buffer.seek(0)
        self.client.set_bucket_versioning(
            bucket_name,
            VersioningConfig(status="Enabled")
        )
        print(file.content_type)
        now = datetime.now().strftime("%Y%m%d%H%M%S%f")
        res = self.client.put_object(
            bucket_name,
            now,
            buffer,
            len(buffer.getvalue()),
            content_type=file.content_type
        )
        print(len(buffer.getvalue()))
        # buffer.close()
        return now, res.version_id
