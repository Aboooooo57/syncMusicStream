import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.responses import JSONResponse, HTMLResponse
from minio.versioningconfig import VersioningConfig

from minio_conf import MinioClient as minioobj
from settings import MINIO_BUCKET_NAME, MINIO_FILE_PATH, CRYPTOGRAPHY_KEY, HOST
from hashlib import sha512
from datetime import datetime
import magic
from io import BytesIO
from cryptography.fernet import Fernet
from minio.error import InvalidResponseError

app = FastAPI()


def hash_file_name(file_name) -> str:
    return sha512((file_name + str(datetime.now())).encode()).hexdigest()


def encrypt_version_id(version_id) -> str:
    f = Fernet(bytes(CRYPTOGRAPHY_KEY, 'utf-8'))
    return f.encrypt(str(version_id).encode()).decode()


def decrypt_version_id(version_id) -> str:
    f = Fernet(bytes(CRYPTOGRAPHY_KEY, 'utf-8'))
    return f.decrypt(str(version_id).encode()).decode()


def is_mp3(buffer: BytesIO) -> bool:
    mime = magic.Magic(mime=True)
    buffer.seek(0)
    buffer_content = buffer.read()
    file_mime_type = mime.from_buffer(buffer_content)
    return file_mime_type == 'audio/mpeg'


async def save_file_to_minio(file: UploadFile):
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
    minioobj.get_client().client.set_bucket_versioning(
        bucket_name,
        VersioningConfig(status="Enabled")
    )
    print(file.content_type)
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    res = minioobj.get_client().client.put_object(
        bucket_name,
        now,
        buffer,
        len(buffer.getvalue()),
        content_type=file.content_type
    )
    print(len(buffer.getvalue()))
    # buffer.close()
    return now, res.version_id


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    object_name, version_id = await save_file_to_minio(file)
    print(version_id, "id")
    print(encrypt_version_id(version_id), "encrypted version_id")
    return {
        "link": HOST + f"/listen/{encrypt_version_id(version_id)}" + ":" + f"{object_name}",
        "filename": file.filename,
        "message": "File uploaded successfully!"}


@app.get("/listen/{token}")
async def listen(token: str):
    try:
        version_id = token.split(":")[0]
        object_name = token.split(":")[-1]
        with minioobj.get_client().client.get_object(bucket_name=MINIO_BUCKET_NAME, object_name=object_name,
                                                     version_id=decrypt_version_id(version_id)) as file_data:
            html_content = file_data.read().decode()
            return HTMLResponse(content=html_content)
    except InvalidResponseError as err:
            return {"error": f"Failed to retrieve file: {err}"}
