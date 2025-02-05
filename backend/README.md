# Backend for ESP32 API

This is the backend for the ESP32 API. It is a REST API that allows the ESP32 to send data to the backend and retrieve data from the backend. The backend is built using FastAPI and PostgreSQL.

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
After installing the dependencies, you can run the backend using the following command:
```bash
python main.py
```

## Apply black formatter
To apply the black formatter to the code, you can run the following command:
```bash
black --config .\pyproject.toml .
```