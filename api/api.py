import asyncio
import json
import os

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse

from minio_conf import MinioClient
from settings import MINIO_BUCKET_NAME, HOST
from hashlib import sha256
from datetime import datetime
from minio.error import InvalidResponseError
from utils import decrypt_version_id, encrypt_version_id
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates"), name="static")


def hash_file_name(file_name) -> str:
    return sha256((file_name + str(datetime.now())).encode()).hexdigest()


def generate_cookie_value():
    random_bytes = os.urandom(32)
    hash_object = sha256(random_bytes)
    return hash_object.hexdigest()


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


event = {}
connected_clients = {}


def check_cookie(request: Request, response: Response):
    usr_cookie = request.cookies.get("usr")
    if not usr_cookie:
        usr_cookie = generate_cookie_value()
        response.set_cookie(key="usr", value=usr_cookie)
    # connected_clients.update({"usr": request.cookies.get("usr")})
    return response, usr_cookie


def init_connected_client(usr_cookie, token):
    # print(token,"token init"*50)
    connected_clients[usr_cookie] = {"client": "", "token": token, "PlayOrPause": False}
    # print(connected_clients)


@app.get("/listen/{token}")
async def listen(request: Request, token: str):
    try:
        link = f"http://{HOST}/stream/{token}"
        html_content = templates.get_template("index.html").render(mp3_url=link, request=request)
        response = HTMLResponse(content=html_content)
        response, usr_cookie = check_cookie(request, response)
        init_connected_client(usr_cookie, token)
        return response
    except InvalidResponseError as err:
        return {"error": f"Failed to retrieve file: {err}"}


@app.get("/stream/{token}")
async def stream(request: Request, token: str):
    try:
        version_id = token.split(":")[0]
        object_name = token.split(":")[-1]

        with MinioClient.get_instance().client.get_object(bucket_name=MINIO_BUCKET_NAME, object_name=object_name,
                                                          version_id=decrypt_version_id(version_id)) as file_data:
            response = Response(content=file_data.read(), media_type="audio/mpeg")
            return response

    except InvalidResponseError as err:
        return {"error": f"Failed to retrieve file {err}"}


async def broadcast_pause(usr, token):
    for other_usr, client_data in connected_clients.items():
        if other_usr != usr and client_data["token"] == token and client_data["PlayOrPause"]:
            await send_pause_event(other_usr)


def broadcast_play(usr, token):
    for other_usr, client_data in connected_clients.items():
        if not other_usr == usr and client_data["token"] == token and not client_data["PlayOrPause"]:
            send_play_event(other_usr)


async def send_pause_event(usr):
    client = connected_clients[usr].get("client")
    global event
    if client:
        # print("sending pause event")
        event = {"event": "pause"}
        # await client.send_event("pause", data={"message": "Music paused"})
    # print("error_pause_event", usr)


def send_play_event(usr):
    client = connected_clients[usr].get("client")
    global event
    if client:
        event = {"event": "play"}
        # client.send_event("play", data={"message": "Music played"})
    # print("error_play_event", usr)


@app.get("/music/play/{token}")
async def play(request: Request, token: str):
    usr = request.cookies.get("usr")
    connected_clients[usr]["PlayOrPause"] = True
    broadcast_play(usr, token)
    return JSONResponse(status_code=200, content={"message": ""})


@app.get("/music/pause/{token}")
async def pause(request: Request, token: str):
    usr = request.cookies.get("usr")
    connected_clients[usr]["PlayOrPause"] = False
    await broadcast_pause(usr, token)
    return JSONResponse(status_code=200, content={"message": ""})


async def event_generator():
    global event
    while True:
        if event != {}:
            yield json.dumps(event)
            event = {}
        await asyncio.sleep(1)  # Example: generate events every second


@app.get("/sse")
async def sse_endpoint(request: Request):
    client_id = request.cookies.get("usr")
    connected_clients[client_id]["client"] = request.scope["client"]
    return EventSourceResponse(event_generator())
