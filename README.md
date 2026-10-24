# Wind forecast monitor

A web app for a UK energy team that buys power on the day-ahead market. It shows:

1. **Day-ahead forecast**: for any delivery day, the latest wind forecast that existed when the buying decision had to be made.
2. **Forecast accuracy**: how far those forecasts were from what wind actually produced, so the error can be allowed for.

Data: Elexon BMRS only. Actuals from `FUELHH` (fuel type `WIND`), forecasts from `WINDFOR`. National level, January 2026.

**Live app:** _add Vercel link here_ (API on Render: _add Render link here_)

> AI tools were used: this project was built with the help of Claude (Anthropic).

## How the forecast is chosen

A purchase for delivery day D is decided on day D-1 at a fixed hour (default 09:00 UTC, which equals UK time in January). For each half hour of day D the app takes the forecast with the latest `publishTime` at or before that moment. The hour can be changed in the page header.

Decisions made in January 2026 (1 to 31 Jan) cover delivery days 2 Jan to 1 Feb. Change `DECISION_FROM` and `DECISION_TO` to use another window.

Error is `forecast - actual`. Positive means the forecast was too high, so wind fell short and extra power had to be bought.

## Files and folders

```
backend/                  FastAPI service
  app/main.py             App setup, CORS, routers
  app/config.py           Settings from environment variables
  app/database.py         Database connection (SQLite locally, Postgres in Docker and when deployed)
  app/models.py           Tables: actuals, forecasts
  app/schemas.py          API response shapes
  app/elexon_client.py    Calls the two Elexon endpoints
  app/loader.py           Downloads the data and stores it (python -m app.loader)
  app/services/forecast_selector.py   Picks the forecast available at decision time
  app/services/metrics.py             Error statistics
  app/routers/forecast.py             /api/meta, /api/forecast
  app/routers/accuracy.py             /api/accuracy
  tests/                  pytest tests
  Dockerfile
frontend/                 React (Vite) app
  src/App.jsx             Header, tabs, decision hour
  src/pages/              Overview.jsx, Accuracy.jsx
  src/components/         Chart.jsx (Apache ECharts wrapper), charts, stats row
  src/api/client.js       Calls to the backend
  src/styles/app.css      Styles, light and dark theme
  Dockerfile, nginx.conf, vercel.json
docker-compose.yml        Postgres + backend + frontend
```

## API

| Endpoint                                           | What it returns                                           |
| -------------------------------------------------- | --------------------------------------------------------- |
| `GET /api/meta`                                    | First and last delivery day available                     |
| `GET /api/forecast?day=2026-01-15&decision_hour=9` | Half-hourly forecast and actual for the day, plus summary |
| `GET /api/accuracy?start=&end=&decision_hour=9`    | Error statistics, by hour, by day, and distribution       |
| `GET /api/health`                                  | Health check                                              |

Interactive docs are at `/docs` on the backend.

## Start the app

### With Docker

```bash
docker compose up --build -d
docker compose exec backend python -m app.loader   # downloads January 2026 data (needs internet)
```

Open http://localhost:3000. API docs: http://localhost:8000/docs.

### Without Docker

Backend (Python 3.11+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.loader            # fills wind.db (SQLite)
uvicorn app.main:app --reload
```

Frontend (Node 20+), in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite forwards `/api` to port 8000.

### Tests

```bash
cd backend && python -m pytest
```

## Deploy

The app runs on three free services: Neon (database), Render (backend), Vercel (frontend). Set them up in this order.

**1. Database on Neon**

1. Sign up at https://neon.tech and create a project.
2. Copy the connection string. It looks like `postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require`.

**2. Load the data into Neon (once, from your computer)**

```bash
cd backend
source .venv/bin/activate                  # Windows: .venv\Scripts\activate
export DATABASE_URL="<neon connection string>"   # Windows PowerShell: $env:DATABASE_URL="<neon connection string>"
python -m app.loader
```

**3. Backend on Render**

1. Push the repo to GitHub. On https://render.com choose **New > Web Service** and connect the repo.
2. Settings: **Root Directory** `backend`, **Runtime** `Docker`, **Instance Type** `Free`, **Health Check Path** `/api/health`.
3. Environment variables:
   - `DATABASE_URL` = the Neon connection string
   - `CORS_ORIGINS` = your Vercel link (add it after step 4, then redeploy)
4. Deploy. The API link looks like `https://<name>.onrender.com`. Check `https://<name>.onrender.com/api/meta` returns the first and last day.

The free Render service sleeps when idle, so the first request after a break can take about a minute. Open the link once before a demo.

**4. Frontend on Vercel**

1. On https://vercel.com choose **Add New > Project** and import the repo.
2. Set **Root Directory** to `frontend`. Vercel detects Vite.
3. Add the environment variable `VITE_API_URL` = the Render link (no trailing slash).
4. Deploy, then put the Vercel link in `CORS_ORIGINS` on Render.

## Settings

| Variable                       | Default                    | Meaning                                                |
| ------------------------------ | -------------------------- | ------------------------------------------------------ |
| `DATABASE_URL`                 | `sqlite:///./wind.db`      | Database                                               |
| `CORS_ORIGINS`                 | `http://localhost:5173`    | Allowed frontend origins, comma separated              |
| `DECISION_HOUR`                | `9`                        | Default decision hour (UTC) on the day before delivery |
| `DECISION_FROM`, `DECISION_TO` | `2026-01-01`, `2026-01-31` | Days on which decisions are made                       |
