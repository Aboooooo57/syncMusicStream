import io

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from minio_conf import MinioClient as minioobj
from settings import MINIO_BUCKET_NAME, MINIO_FILE_PATH
from hashlib import sha512
from datetime import datetime
import magic
from io import BytesIO

app = FastAPI()


def hash_file_name(file_name) -> str:
    return sha512((file_name + str(datetime.now())).encode()).hexdigest()


def is_mp3(buffer: BytesIO) -> bool:
    mime = magic.Magic(mime=True)
    buffer.seek(0)
    buffer_content = buffer.read()
    file_mime_type = mime.from_buffer(buffer_content)
    return file_mime_type == 'audio/mpeg'


async def save_file_to_minio(file: UploadFile):
    # Set your Minio bucket name
    bucket_name = MINIO_BUCKET_NAME

    # Initialize BytesIO buffer
    buffer = BytesIO()

    # Write the file data to BytesIO buffer
    while True:
        chunk = await file.read(1024)  # Read 1 KB at a time
        if not chunk:
            break
        buffer.write(chunk)

    # Reset buffer position to start
    hashed_file_name = hash_file_name(file.filename)
    object_name = hashed_file_name

    if not is_mp3(buffer):
        raise HTTPException(status_code=400, detail="Uploaded file is not an MP3")

    buffer.seek(0)

    # Upload the file to Minio
    minioobj.get_client().client.put_object(
        bucket_name,
        object_name + file.filename,
        buffer,
        len(buffer.getvalue()),  # Specify the size of the data in the buffer
        content_type=file.content_type  # Set the content type
    )
    print(len(buffer.getvalue()))


# async def save_file_to_minio(file: UploadFile):
#     # Set your Minio bucket name
#     bucket_name = MINIO_BUCKET_NAME
#
#     # Set the buffer size for streaming (adjust as needed)
#     buffer_size = 1024 * 1024  # 1 MB
#
#     # Initialize variables
#     total_bytes_written = 0
#
#     # Write the file data to Minio in chunks
#     with minioobj.get_client().client.put_object(bucket_name, file.filename, file.file, file.size,
#                                                  content_type=file.content_type) as result:
#         # Iterate over the file chunks and write them to Minio
#         while True:
#             chunk = await file.read(buffer_size)
#             if not chunk:
#                 break
#             total_bytes_written += len(chunk)
#             result.write(chunk)
#
#     # Print the total bytes written (optional)
#     print(f"Total bytes written: {total_bytes_written}")


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    await save_file_to_minio(file)
    return {"filename": file.filename, "message": "File uploaded successfully to Minio!"}
#
# @app.post("/uploadfile/")
# async def upload_file(file: UploadFile = File(...)):
#
#     contents = await file.read()
#     if not is_mp3(contents):
#         raise HTTPException(status_code=400, detail="Uploaded file is not an MP3")
#
#     minio_client = minioobj.get_client().client
#     hashed_file_name = hash_file_name(file.filename)
#     object_name = hashed_file_name
#
#     # Read file data
#     file_data = await file.read()
#     file_size = file.size
#
#     print(dir(file))
#     print(dir(file.file),"filesize")
#     print(type(file.file),"readdd")
#     print(dir(file))
#     print(file.size)
#     response = minio_client.put_object(
#             MINIO_BUCKET_NAME,
#             object_name,
#             io.BytesIO(file_data),
#             file_size,
#             content_type=file.content_type
#     )
#     print(dir(response))
#     print(response.location)
#     print(response.object_name)
#     print(response.bucket_name)
#     return {"message": "File uploaded successfully"}
#     # Ensure that the object is uploaded successfully
# if response.status == 200:
#
# else:
#     return {"message": "Failed to upload file"}


# print(file,"file")
# print(dir(file),"dirfile")
# print(dir(file.file))
# minio_client.upload_file(bucket_name=MINIO_BUCKET_NAME, object_name=hashed_file_name,file_path=file)
#
# return JSONResponse(content={"filename": hashed_file_name, "status": "uploaded"})
