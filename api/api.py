import os

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, Response

from minio_conf import MinioClient
from settings import MINIO_BUCKET_NAME, HOST
from hashlib import sha256
from datetime import datetime
from minio.error import InvalidResponseError
from utils import decrypt_version_id, encrypt_version_id
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates"), name="static")


def hash_file_name(file_name) -> str:
    return sha256((file_name + str(datetime.now())).encode()).hexdigest()


def generate_cookie_value(version_id):
    return f"{version_id}:{sha256(os.urandom(18)).hexdigest()}"


@app.get("/upload")
async def upload():
    try:
        html_content = templates.get_template("upload.html").render()
        response = HTMLResponse(content=html_content)
        return response
    except InvalidResponseError as err:
        return {"error": f"Failed to retrieve file: {err}"}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    object_name, version_id = await MinioClient.get_instance().save_file_to_minio(file)
    return {
        "link": "http://" + HOST + f"/listen/{encrypt_version_id(version_id)}" + ":" + f"{object_name}",
        "filename": file.filename,
        "message": "File uploaded successfully!"}


def check_cookie(request: Request, response: Response, version_id: str):
    if not request.cookies.get("usr"):
        response.set_cookie(key="usr", value=generate_cookie_value(version_id))
    return response


@app.get("/listen/{token}")
async def listen(request: Request, token: str):
    try:
        link = f"http://{HOST}/stream/{token}"
        html_content = templates.get_template("index.html").render(mp3_url=link, request=request)
        response = HTMLResponse(content=html_content)
        response = check_cookie(request, response, token.split(":")[0])

        return response
    except InvalidResponseError as err:
        return {"error": f"Failed to retrieve file: {err}"}


@app.get("/stream/{token}")
async def stream(token: str):
    try:
        version_id = token.split(":")[0]
        object_name = token.split(":")[-1]
        with MinioClient.get_instance().client.get_object(bucket_name=MINIO_BUCKET_NAME, object_name=object_name,
                                                          version_id=decrypt_version_id(version_id)) as file_data:
            response = Response(content=file_data.read(), media_type="audio/mpeg")
            return response
    except InvalidResponseError as err:
        return {"error": f"Failed to retrieve file {err}"}
