import os
from dotenv import load_dotenv

load_dotenv()

SOCKET_SERVER = os.getenv('SOCKET_SERVER')
SOCKET_SERVER_PORT = os.getenv('SOCKET_SERVER_PORT')

