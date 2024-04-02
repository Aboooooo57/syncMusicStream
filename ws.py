import asyncio
import websockets
from settings import SOCKET_SERVER, SOCKET_SERVER_PORT


async def setup_websocket_server():
    host = SOCKET_SERVER
    port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()


async def start_websocket_server():
    await setup_websocket_server()


connected_clients = {}


async def broadcast_status(device_id,status):
    global connected_clients
    print(connected_clients)
    for other_id, other_data in connected_clients.items():
        if status is True:
            print("Broadcasting status for device", device_id, "to", other_id)
            message = f"playing:{device_id}"
            print(other_id != device_id,"other_id != device_id")
            print(connected_clients[other_id]["PlayOrPause"] is False,"connected_clients[other_id]is False")
            if other_id != device_id and connected_clients[other_id]["PlayOrPause"] is False:
                await other_data["websocket"].send(message)
        else:
            message = f"paused:{device_id}"
            if other_id != device_id and connected_clients[other_id]["PlayOrPause"] is True:
                await other_data["websocket"].send(message)


async def websocket_handler(websocket, path):
    global connected_clients
    async for message in websocket:
        print(f"Received message: {message}")
        if message.startswith("REGISTER_DEVICE:"):
            device_id = message.split(":")[1]
            connected_clients[device_id] = {"websocket": websocket, "position": None, "PlayOrPause": False}
            print(f"Device {device_id} connected.")
        elif message.startswith("UPDATE_POSITION:"):
            parts = message.split(":")
            device_id = parts[1]
            position = float(parts[2])
            connected_clients[device_id]["position"] = position
            print(f"Device {device_id} updated position: {position}")
            await broadcast_positions()
        elif message.startswith("PLAY:"):
            parts = message.split(":")
            device_id = parts[1]
            connected_clients[device_id]["PlayOrPause"] = True
            print(f"Device {device_id} playing.")
            await broadcast_status(device_id,True)
        elif message.startswith("PAUSE:"):
            parts = message.split(":")
            device_id = parts[1]
            connected_clients[device_id]["PlayOrPause"] = False
            print(f"Device {device_id} paused.")
            await broadcast_status(device_id,False)
        elif message.startswith("SYNC_MUSIC:"):
            parts = message.split(":")
            device_id = parts[1]


async def broadcast_positions():
    global connected_clients
    for device_id, data in connected_clients.items():
        position = data.get("position")
        if position is not None:
            message = f"position_update:{device_id}:{position}"
            for other_id, other_data in connected_clients.items():
                if other_id != device_id:
                    await other_data["websocket"].send(message)
