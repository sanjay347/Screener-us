# Screener·US — Stock Research Platform

A Screener.in-style stock research app for US markets built with FastAPI + vanilla HTML/JS.

## Features
- Full financials (P&L, Balance Sheet, Cash Flow — annual & quarterly)
- Interactive price chart with OHLCV hover, 50/200 DMA, volume
- Peer comparison
- Shareholding pattern
- Earnings history, dividends, analyst recommendations
- Firebase Auth (Google + Email/Password)
- Watchlist synced via Firebase Realtime Database

## Project Structure
```
screener/
├── frontend/
│   └── index.html        # Single-page app (no build step)
├── backend/
│   ├── main.py           # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile        # For Railway / Cloud Run
│   └── railway.toml
├── firebase.json         # Firebase Hosting config
├── deploy.sh             # One-click deploy script
└── start.sh              # Local dev start script
```

## Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
Open `frontend/index.html` in your browser (or serve with any static server).

## Deployment

### Backend → Railway
1. Connect this GitHub repo to [Railway](https://railway.app)
2. Set root directory to `/backend`
3. Railway auto-detects the Dockerfile and deploys
4. Copy the Railway URL

### Frontend → Firebase Hosting
1. Update `const API` in `frontend/index.html` with your Railway URL
2. Run `./deploy.sh`

## Tech Stack
- **Backend:** Python, FastAPI, yfinance, pandas
- **Frontend:** Vanilla HTML/CSS/JS, Chart.js
- **Auth:** Firebase Authentication
- **Database:** Firebase Realtime Database (watchlist)
- **Hosting:** Firebase Hosting (frontend) + Railway (backend)
