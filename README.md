# FastAPI Synchronous Music Streaming with WebSocket

A basic implementation of a FastAPI application for synchronous music streaming across devices with WebSocket support using MinIO storage.

## Project Information

- **Version**: 0.0.5  
- **Author**: Abolfazl Saeedi  
- **License**: MIT  

## Requirements

- Docker  
- Docker Compose  

## Environment Variables

- `MINIO_BUCKET_NAME`: Name of the MinIO bucket.  
- `HOST`: Hostname or IP address of the service.  

## Directory Structure

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

## Setup with Docker

### Prerequisites

- Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).

### Steps

1. Clone the repository:  
   ```bash
   git clone https://github.com/Aboooooo57/syncMusicStream.git
   cd syncMusicStream
   ```
2.	Edit .env.example to .env file in the project root and configure the required environment variables
3.	Build and start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
4.	Access the application:
	•	File upload form: http://localhost:8000/upload

Contact
For support or inquiries, contact:
Email: abolfazl.saeedi9775@gmail.com
