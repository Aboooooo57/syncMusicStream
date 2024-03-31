import os
from dotenv import load_dotenv

load_dotenv()

SOCKET_SERVER = os.getenv('SOCKET_SERVER')
SOCKET_SERVER_PORT = os.getenv('SOCKET_SERVER_PORT')

HTTP_SERVER = os.getenv('HTTP_SERVER')
HTTP_SERVER_PORT = os.getenv('HTTP_SERVER_PORT')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
MINIO_FILE_PATH=os.getenv('MINIO_FILE_PATH')

CRYPTOGRAPHY_KEY= os.getenv('CRYPTOGRAPHY_KEY')

HOST = os.getenv('HOST')