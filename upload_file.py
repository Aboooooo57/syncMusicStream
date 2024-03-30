from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from minio_conf import MinioClient as minioobj
from settings import MINIO_BUCKET_NAME
from hashlib import sha512
from datetime import datetime
import magic

app = FastAPI()


def hash_file_name(file_name) -> str:
    return sha512((file_name + str(datetime.now())).encode()).hexdigest()

def is_mp3(file: bytes) -> bool:
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file)
    return file_type == 'audio/mpeg'


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()
    if not is_mp3(contents):
        raise HTTPException(status_code=400, detail="Uploaded file is not an MP3")

    minio_client = minioobj.get_client()
    hashed_file_name = hash_file_name(file.filename)
    minio_client.upload_file(bucket_name=MINIO_BUCKET_NAME, filename=hashed_file_name)

    return JSONResponse(content={"filename": hashed_file_name, "status": "uploaded"})
