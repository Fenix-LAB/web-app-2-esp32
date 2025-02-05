# Web App to send and receive data to ESP32

## Description
This is a web app that allows you to send and receive data to an ESP32. The ESP32 is programmed to connect to a WiFi network.

- API: FastAPI located in AWS server
- Frontend: Vue.js, javascript, HTML, CSS
- ESP32: C++
- Database: PostgreSQL

## Features
- Send data to ESP32
- Receive data from ESP32
- Store data in database
- Display data in a table

## Run locally
### API
1. Create a virtual environment
```bash
python -m venv .venv
```

2. Activate the virtual environment
```bash
. .venv/Scripts/activate
```

3. Install the requirements
```bash
pip install -r requirements.txt
```

4. Run the API
```bash
python main.py
```

### Frontend
1. Install the dependencies
```bash
npm install
```

2. Run the frontend
```bash
npm run dev
```

### Database
No implemented yet

### ESP32
No implemented yet
