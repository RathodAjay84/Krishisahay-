Updated project version 🚀

# KrishiSahay

KrishiSahay is a Streamlit smart agriculture assistant for Telangana farmers.

## Features

- Crop recommendation using soil, season, rainfall, humidity, and temperature
- Crop-health image assessment with Gemini Vision
- Soil-health analysis
- Fertilizer guidance
- Weather and market views
- Government scheme information
- AI farming assistant with browser voice input
- Responsive agri-tech dashboard with charts, alerts, and history

## Setup on another laptop

Use Python 3.11 or 3.12 for the smoothest compatibility with the machine-learning packages.

Clone the repository first:

```powershell
git clone https://github.com/RathodAjay84/AGROWEALTH.git
cd AGROWEALTH
```

Create a virtual environment and install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Add API keys to `.env` locally. Never commit `.env`.

The app still opens without API keys, but Gemini chat, live weather, and image
analysis require valid keys. Never copy your private `.env` file to GitHub or
send it to another person.

## Run

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Common fixes

If `streamlit` is not recognized, always run it through the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If a port is busy, use another one:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8507
```
