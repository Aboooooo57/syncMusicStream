from io import BytesIO

import magic
from cryptography.fernet import Fernet

from settings import CRYPTOGRAPHY_KEY


def is_mp3(buffer: BytesIO) -> bool:
    mime = magic.Magic(mime=True)
    buffer.seek(0)
    buffer_content = buffer.read()
    file_mime_type = mime.from_buffer(buffer_content)
    return file_mime_type == 'audio/mpeg'


def decrypt_version_id(version_id) -> str:
    f = Fernet(bytes(CRYPTOGRAPHY_KEY, 'utf-8'))
    return f.decrypt(str(version_id).encode()).decode()


def encrypt_version_id(version_id) -> str:
    f = Fernet(bytes(CRYPTOGRAPHY_KEY, 'utf-8'))
    return f.encrypt(str(version_id).encode()).decode()
