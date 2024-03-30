import http.server
import socketserver
import os
import threading
import websockets
import asyncio

from minio_conf import MinioClient
from settings import SOCKET_SERVER,SOCKET_SERVER_PORT,HTTP_SERVER,HTTP_SERVER_PORT


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        if self.path.endswith('.mp3'):
            self.send_response(200)
            self.send_header('Content-type', 'audio/mpeg')
            self.end_headers()
            with open(os.path.join(os.getcwd(), self.path[1:]), 'rb') as f:
                self.wfile.write(f.read())
        else:
            return super().do_GET()

# Set up the WebSocket server
async def setup_websocket_server():
    host = SOCKET_SERVER
    port = int(SOCKET_SERVER_PORT) if isinstance(SOCKET_SERVER_PORT, str) else SOCKET_SERVER_PORT
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()


# Function to start the WebSocket server in a separate thread
def start_websocket_server():
    asyncio.run(setup_websocket_server())


# Start the WebSocket server in a separate thread
threading.Thread(target=start_websocket_server).start()

# Dictionary to store connected clients (devices) and their playback positions
connected_clients = {}


async def broadcast_status(status):
    global connected_clients
    for device_id, data in connected_clients.items():
        message = f"playing:{device_id}" if status is True else f"paused:{device_id}"
        for other_id, other_data in connected_clients.items():
            if other_id != device_id:
                await other_data["websocket"].send(message)


async def websocket_handler(websocket, path):
    global connected_clients
    async for message in websocket:
        print(f"Received message: {message}")
        if message.startswith("REGISTER_DEVICE:"):
            # Register device with unique ID
            device_id = message.split(":")[1]
            connected_clients[device_id] = {"websocket": websocket, "position": None}
            print(f"Device {device_id} connected.")
        elif message.startswith("UPDATE_POSITION:"):
            # Update playback position for the device
            parts = message.split(":")
            device_id = parts[1]
            position = float(parts[2])
            connected_clients[device_id]["position"] = position
            print(f"Device {device_id} updated position: {position}")
            await broadcast_positions()

        elif message.startswith("PLAY"):
            parts = message.split(":")
            device_id = parts[1]
            connected_clients[device_id]["PlayOrPause"] = True
            print(f"Device {device_id} playing.")
            await broadcast_status(True)

        elif message.startswith("PAUSE"):
            parts = message.split(":")
            device_id = parts[1]
            connected_clients[device_id]["PlayOrPause"] = False
            print(f"Device {device_id} paused.")
            await broadcast_status(False)


# Function to broadcast playback positions to all connected devices
async def broadcast_positions():
    global connected_clients
    for device_id, data in connected_clients.items():
        position = data.get("position")
        if position is not None:
            message = f"POSITION_UPDATE:{device_id}:{position}"
            for other_id, other_data in connected_clients.items():
                if other_id != device_id:
                    await other_data["websocket"].send(message)


# Set up the HTTP server
PORT = int(HTTP_SERVER_PORT) if isinstance(HTTP_SERVER_PORT, str) else HTTP_SERVER_PORT
Handler = MyHttpRequestHandler
http_server = socketserver.TCPServer((HTTP_SERVER, PORT), Handler)

def main():
    MinioClient.first_run()

    try:
        print("Serving at port", PORT)
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.shutdown()
        http_server.server_close()

if __name__ == "__main__":
    main()
