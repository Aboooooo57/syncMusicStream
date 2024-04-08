from minio_conf import MinioClient


def main():
    MinioClient.get_instance().initialize()


if __name__ == "__main__":
    main()
