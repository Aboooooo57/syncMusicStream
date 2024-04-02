import asyncio
import threading

from minio_conf import MinioClient
from settings import MINIO_BUCKET_NAME
from ws import start_websocket_server


async def main_async():
    MinioClient.get_instance().initialize()
    await start_websocket_server()


def main():
    asyncio.run(main_async())

    # MinioClient.get_client().list_buckets()
    # objs = MinioClient.get_instance().list_objects(MINIO_BUCKET_NAME)
    # for obj in objs:
    # # print(obj.object_name)
    # # print(obj.version_id)
    # # print(obj.size)
    # # print(obj.tags)
    # # print(obj.content_type)
    # # print(dir(obj))
    # # print(MinioClient.get_client().client.(bucket_name=MINIO_BUCKET_NAME,))
    # print(MinioClient.get_instance().client.get_presigned_url(method="GET", bucket_name=MINIO_BUCKET_NAME,
    #                                                           object_name=obj.object_name, version_id=obj.version_id))


if __name__ == "__main__":
    main()
    asyncio.Future()
