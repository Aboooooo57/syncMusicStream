import asyncio
import websockets
from settings import SOCKET_SERVER, SOCKET_SERVER_PORT


async def connect_or_reconnect(websocket_connection):
    # Check if the WebSocket connection is open
    if websocket_connection and websocket_connection.open:
        return True  # WebSocket connection is open
    else:
        try:
            host = SOCKET_SERVER
            port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
            websocket_connection = await websockets.connect(f"ws://{host}:{port}")
            return True  # WebSocket connection established successfully
        except Exception as e:
            # Handle connection errors
            print(f"Failed to connect to WebSocket server: {e}")
            return False  # Failed to establish WebSocket connection


async def setup_websocket_server():
    host = SOCKET_SERVER
    port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()


async def start_websocket_server():
    await setup_websocket_server()


connected_clients = {}


async def broadcast_status(device_id, status):
    global connected_clients
    # print(connected_clients)
    for other_id, other_data in connected_clients.items():
        if status is True:
            message = f"playing:{device_id}"
            if other_id != device_id and connected_clients[other_id]["PlayOrPause"] is False:
                if await connect_or_reconnect(other_data["websocket"]):
                    await other_data["websocket"].send(message)
                    print("Broadcasting status is OKK")
                else:
                    print("Broadcasting status Failed")
        else:
            message = f"paused:{device_id}"
            if other_id != device_id and connected_clients[other_id]["PlayOrPause"] is True:
                if await connect_or_reconnect(other_data["websocket"]):
                    await other_data["websocket"].send(message)
                    print("Broadcasting status is OKK")
                else:
                    print("Broadcast status Failed")


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
            await broadcast_status(device_id, True)
        elif message.startswith("PAUSE:"):
            parts = message.split(":")
            device_id = parts[1]
            connected_clients[device_id]["PlayOrPause"] = False
            print(f"Device {device_id} paused.")
            await broadcast_status(device_id, False)
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
