# FastAPI Synchronous Music Streaming with WebSocket

A basic implementation of a FastAPI application for synchronous music streaming across devices with WebSocket support using MinIO storage.

## Project Information

- **Version**: 1.0.0  
- **Author**: Abolfazl Saeedi  
- **License**: MIT  

## Requirements

- Python >= 3.9  
- FastAPI >= 0.95.2  
- Jinja2 >= 3.1.2  
- Uvicorn >= 0.22.0  
- MinIO >= 7.1.15  
- Websockets >= 10.4  

## Setup

### Environment Variables

- `MINIO_BUCKET_NAME`: Name of the MinIO bucket.  
- `HOST`: Hostname or IP address of the service.  

### Directory Structure

- `templates/`: Contains Jinja2 templates (e.g., `upload.html`, `index.html`).  
- `templates/static/`: Contains static files (e.g., CSS, JavaScript, images).  
- `utils.py`: Helper functions for encryption/decryption.  
- `minio_conf.py`: Configuration for the MinIO client.  
- `settings.py`: Application settings and constants.  

## Endpoints

- `/upload`: Displays the file upload HTML form.  
- `/uploadfile/`: Handles file upload and saves it to MinIO.  
- `/listen/{token}`: Displays the audio player for the requested file token.  
- `/stream/{token}`: Streams the requested file as an audio response.  
- `/ws`: WebSocket endpoint for real-time music streaming updates.  

## Features

- **Basic file upload**: Upload files to MinIO securely.  
- **Real-time music streaming**: Stream audio across devices via WebSocket.  
- **Token-based access**: Securely access uploaded files using tokens.  
- **User identity tracking**: Use cookies to track user sessions.  

## Usage

1. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
2.	Set environment variables for MINIO_BUCKET_NAME and HOST.
3.	Run the application:
   ```bash
   unicorn main:app --reload
   ```
4.	Access the file upload form at:
    http://localhost:8000/upload.

For support or inquiries, contact:
Email: abolfazl.saeedi9775@gmail.com
