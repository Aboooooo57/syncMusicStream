
FROM python:3.9
LABEL authors="EbiSaeidi"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
CMD ["sh", "-c", "python main.py && uvicorn api:app --host 0.0.0.0 --port 8000"]

