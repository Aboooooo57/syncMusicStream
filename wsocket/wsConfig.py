import asyncio
import websockets
from settings import SOCKET_SERVER, SOCKET_SERVER_PORT


async def connect_or_reconnect(websocket_connection):
    if websocket_connection and websocket_connection.open:
        return True
    else:
        try:
            host = SOCKET_SERVER
            port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
            websocket_connection = await websockets.connect(f"ws://{host}:{port}")
            return True
        except Exception as e:

            print(f"Failed to connect to WebSocket server: {e}")
            return False


async def setup_websocket_server():
    host = SOCKET_SERVER
    port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()


async def start_websocket_server():
    await setup_websocket_server()


connected_clients = {}


async def broadcast_status(usr_cookie, status):
    global connected_clients
    parts = usr_cookie.split(":")
    version_id = parts[0]
    device_id = parts[1]
    print(status)
    for other_id, other_data in connected_clients.items():
        print(other_id != f"{version_id}:{device_id}", "first" * 4)
        print(connected_clients[other_id]["PlayOrPause"], "second" * 10)
        print(version_id == other_id.split(":")[0], "last" * 5)
        print(other_id.split(":")[0])
        print(version_id,"version_id"*3)
        if status is True:
            message = f"playing:{version_id}:{device_id}"
            if other_id != f"{version_id}:{device_id}" and connected_clients[other_id]["PlayOrPause"] is False and (
                    version_id == other_id.split(":")[0]):
                if await connect_or_reconnect(other_data["wsocket"]):
                    await other_data["wsocket"].send(message)
                    print("Broadcasting status is OKK")
                else:
                    print("Broadcasting status Failed")
        else:
            message = f"paused:{version_id}:{device_id}"
            if other_id != f"{version_id}:{device_id}" and connected_clients[other_id]["PlayOrPause"] is True and (
                    version_id == other_id.split(":")[0]):
                if await connect_or_reconnect(other_data["wsocket"]):
                    await other_data["wsocket"].send(message)
                    print("Broadcasting status is OKK")
                else:
                    print("Broadcast status Failed")


async def websocket_handler(websocket, path):
    global connected_clients
    async for message in websocket:
        parts = message.split(":")
        print(f"Received message: {message}")
        if message.startswith("REGISTER_DEVICE:"):
            print(message)
            device_id = parts[1] + ":" + parts[2]
            connected_clients[device_id] = {"wsocket": websocket, "position": None, "PlayOrPause": False}
            print(f"Device {device_id} connected.")
        elif message.startswith("UPDATE_POSITION:"):
            device_id = parts[1]
            position = float(parts[2])
            connected_clients[device_id]["position"] = position
            print(f"Device {device_id} updated position: {position}")
            await broadcast_positions()
        elif message.startswith("PLAY:"):
            usr_cookie = parts[1] + ":" + parts[2]
            connected_clients[usr_cookie]["PlayOrPause"] = True
            print(f"Device {usr_cookie} playing.")
            await broadcast_status(usr_cookie, True)
        elif message.startswith("PAUSE:"):
            usr_cookie = parts[1] + ":" + parts[2]
            connected_clients[usr_cookie]["PlayOrPause"] = False
            print(f"Device {usr_cookie} paused.")
            await broadcast_status(usr_cookie, False)
        elif message.startswith("SYNC_MUSIC:"):
            device_id = parts[1]


async def broadcast_positions():
    global connected_clients
    for device_id, data in connected_clients.items():
        position = data.get("position")
        if position is not None:
            message = f"position_update:{device_id}:{position}"
            for other_id, other_data in connected_clients.items():
                if other_id != device_id:
                    await other_data["wsocket"].send(message)
