# import http.server
# import socketserver
# import os
# import socket
# import time
# import threading
# import websocket
#
# class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         if self.path == "/":
#             self.path = "/index.html"
#         if self.path.endswith('.mp3'):
#             self.send_response(200)
#             self.send_header('Content-type', 'audio/mpeg')
#             self.end_headers()
#             with open(os.path.join(os.getcwd(), self.path[1:]), 'rb') as f:
#                 self.wfile.write(f.read())
#         else:
#             return super().do_GET()
#
# WEBSOCKET_SERVER = "ws://localhost:8000"
#
# def ws_config():
#     ws = websocket.WebSocketApp(WEBSOCKET_SERVER, on_message=on_message)
#     ws.run_forever()
#
# def on_message(ws, message):
#     if message.startswith("MASTER_POSITION:"):
#         playback_position = float(message.split(":")[1])
#         print("Master playback position:", playback_position)
#     elif message.startswith("SLAVE_POSITION:"):
#         playback_position = float(message.split(":")[1])
#         print("Slave playback position:", playback_position)
#
# def socket_config():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_address = ('localhost', 12345)
#     server_socket.bind(server_address)
#     server_socket.listen()
#     print("Waiting for slave devices to connect...")
#     while True:
#         connection, client_address = server_socket.accept()
#         slave_thread = threading.Thread(target=handle_slave_connection, args=(connection, client_address))
#         slave_thread.start()
#
# def handle_slave_connection(connection, client_address):
#     print("Connected to slave device:", client_address)
#     try:
#         send_sync_signal(connection)
#     finally:
#         connection.close()
#
# def get_current_position():
#     pass
#
# def send_sync_signal(client_socket):
#     while True:
#         current_position = get_current_position()
#         timestamp = time.time()
#         message = f"SYNC:{timestamp}:{current_position}"
#         client_socket.sendall(message.encode())
#         time.sleep(1)
#
# PORT = 8000
# Handler = MyHttpRequestHandler
# http_server = socketserver.TCPServer(("", PORT), Handler)
#
# try:
#     threading.Thread(target=ws_config).start()
#     threading.Thread(target=socket_config).start()
#
#     print("Serving at port", PORT)
#     http_server.serve_forever()
# except KeyboardInterrupt:
#     http_server.shutdown()
#     http_server.server_close()

import http.server
import socketserver
import os
import socket
import time
import threading
import websockets
import asyncio

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

# Function to handle WebSocket messages from clients
async def websocket_handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        if message.startswith("MASTER_POSITION:"):
            playback_position = float(message.split(":")[1])
            print("Master playback position:", playback_position)
        elif message.startswith("SLAVE_POSITION:"):
            playback_position = float(message.split(":")[1])
            print("Slave playback position:", playback_position)

# Set up the WebSocket server
async def setup_websocket_server():
    host = "localhost"
    port = 8001
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()

# Function to start the WebSocket server in a separate thread
def start_websocket_server():
    asyncio.run(setup_websocket_server())

# Start the WebSocket server in a separate thread
threading.Thread(target=start_websocket_server).start()

# Set up the HTTP server
PORT = 8000
Handler = MyHttpRequestHandler
http_server = socketserver.TCPServer(("", PORT), Handler)

try:
    print("Serving at port", PORT)
    http_server.serve_forever()
except KeyboardInterrupt:
    http_server.shutdown()
    http_server.server_close()
