from datetime import date

import httpx

from app import loader
from app.config import settings
from app.models import Actual, Forecast


def fake_elexon(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/FUELHH/stream"):
        return httpx.Response(
            200,
            json=[
                {"fuelType": "WIND", "startTime": "2026-01-02T00:00:00Z", "generation": 5000},
                {"fuelType": "WIND", "startTime": "2026-01-02T00:30:00Z", "generation": 5100},
                {"fuelType": "NUCLEAR", "startTime": "2026-01-02T00:00:00Z", "generation": 4000},
                {"fuelType": "WIND", "startTime": "2026-02-20T00:00:00Z", "generation": 1},
            ],
        )
    return httpx.Response(
        200,
        json=[
            {"publishTime": "2026-01-01T08:00:00.123Z", "startTime": "2026-01-02T00:00:00Z", "generation": 4800},
            {"publishTime": "2026-01-01T08:00:00.123Z", "startTime": "2026-01-02T00:30:00Z", "generation": None},
            {"publishTime": "2026-01-01T08:00:00.123Z", "startTime": "2025-12-30T00:00:00Z", "generation": 7},
        ],
    )


def test_load_keeps_only_wind_in_window(monkeypatch, db):
    monkeypatch.setattr(settings, "decision_from", date(2026, 1, 1))
    monkeypatch.setattr(settings, "decision_to", date(2026, 1, 1))

    client = httpx.Client(transport=httpx.MockTransport(fake_elexon))
    actuals, forecasts = loader.load(client)

    assert (actuals, forecasts) == (2, 1)
    assert db.query(Actual).count() == 2
    assert db.query(Forecast).one().generation == 4800
