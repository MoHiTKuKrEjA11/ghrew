"""Download Elexon data for the configured decision window and store it.

Run with:  python -m app.loader
"""
from datetime import datetime, time, timedelta

import httpx

from .config import settings
from .database import Base, SessionLocal, engine
from .elexon_client import fetch_actuals, fetch_forecasts
from .models import Actual, Forecast
from .services.forecast_selector import clear_cache

BATCH = 5000


def _insert(db, model, rows: list[dict]):
    for i in range(0, len(rows), BATCH):
        db.bulk_insert_mappings(model, rows[i : i + BATCH])


def load(client: httpx.Client | None = None) -> tuple[int, int]:
    Base.metadata.create_all(engine)
    client = client or httpx.Client(timeout=120)

    # A decision on day D covers delivery day D+1.
    delivery_start = datetime.combine(settings.decision_from + timedelta(days=1), time(0))
    delivery_end = datetime.combine(settings.decision_to + timedelta(days=2), time(0))
    last_cutoff = datetime.combine(settings.decision_to, time(settings.decision_hour))
    publish_from = datetime.combine(settings.decision_from - timedelta(days=2), time(0))

    actuals = fetch_actuals(client, delivery_start.date(), (delivery_end - timedelta(days=1)).date())
    forecasts = fetch_forecasts(client, publish_from, last_cutoff)

    actual_rows = [
        {"start_time": t, "generation": g} for t, g in actuals.items() if delivery_start <= t < delivery_end
    ]
    forecast_rows = [
        {"start_time": s, "publish_time": p, "generation": g}
        for (s, p), g in forecasts.items()
        if delivery_start <= s < delivery_end
    ]

    with SessionLocal() as db:
        db.query(Actual).delete()
        db.query(Forecast).delete()
        _insert(db, Actual, actual_rows)
        _insert(db, Forecast, forecast_rows)
        db.commit()

    clear_cache()
    return len(actual_rows), len(forecast_rows)


if __name__ == "__main__":
    a, f = load()
    print(f"Loaded {a} actual rows and {f} forecast rows")
