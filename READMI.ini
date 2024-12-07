[Project]
Name = FastAPI Synchronous Music Streaming with WebSocket
Description = A basic implementation of a FastAPI application for synchronous music streaming across devices with WebSocket support using MinIO storage.
Version = 1.0.0
Author = Abolfazl Saeedi
License = MIT

[Requirements]
Python = >=3.9
FastAPI = >=0.95.2
Jinja2 = >=3.1.2
uvicorn = >=0.22.0
minio = >=7.1.15
websockets = >=10.4

[Setup]
EnvironmentVariables =
    MINIO_BUCKET_NAME : Name of the MinIO bucket
    HOST : Hostname or IP address of the service

[DirectoryStructure]
templates/ = Contains Jinja2 templates (e.g., `upload.html`, `index.html`)
templates/static/ = Contains static files (e.g., CSS, JavaScript, images)
utils.py = Helper functions for encryption/decryption
minio_conf.py = Configuration for the MinIO client
settings.py = Application settings and constants

[Endpoints]
/upload = Displays the file upload HTML form.
/uploadfile/ = Handles file upload and saves it to MinIO.
/listen/{token} = Displays the audio player for the requested file token.
/stream/{token} = Streams the requested file as an audio response.
/ws = WebSocket endpoint for real-time music streaming updates.

[Features]
- Basic file upload to MinIO.
- Real-time music streaming via WebSocket.
- Token-based access for files.
- User identity tracking with cookies.

[Usage]
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables for `MINIO_BUCKET_NAME` and `HOST`.
3. Run the application using Uvicorn: `uvicorn main:app --reload`
4. Access the file upload form at `http://localhost:8000/upload`.
5. Connect to the WebSocket at `ws://localhost:8000/ws` for real-time music streaming.

[Notes]
- Ensure MinIO is properly configured and running.
- Replace `MINIO_BUCKET_NAME` and `HOST` with appropriate environment values.
- Modify WebSocket handling in `main.py` for specific music streaming logic.
- Customize error handling and logging as necessary for production use.

[Contact]
SupportEmail = abolfazl.saeedi9775@gmail.com