from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models import Actual, Forecast

client = TestClient(app)


def seed(db, days=3):
    start = datetime(2026, 1, 2)
    for i in range(days * 48):
        t = start + timedelta(minutes=30 * i)
        cutoff = datetime.combine(t.date() - timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
        db.add(Forecast(start_time=t, publish_time=cutoff - timedelta(hours=1), generation=1000 + i))
        db.add(Forecast(start_time=t, publish_time=cutoff + timedelta(hours=1), generation=9999))
        db.add(Actual(start_time=t, generation=1000 + i - 100))
    db.commit()


def test_empty_database(db):
    assert client.get("/api/meta").json()["first_day"] is None
    assert client.get("/api/accuracy").status_code == 404
    assert client.get("/api/forecast", params={"day": "2026-01-02"}).status_code == 404


def test_meta_and_day_forecast(db):
    seed(db)
    meta = client.get("/api/meta").json()
    assert (meta["first_day"], meta["last_day"]) == ("2026-01-02", "2026-01-04")

    body = client.get("/api/forecast", params={"day": "2026-01-03"}).json()
    assert len(body["points"]) == 48
    assert body["decision_time"] == "2026-01-02T09:00:00Z"
    assert body["points"][0]["forecast"] == 1048  # the forecast published after the cutoff is ignored
    assert body["band_mw"] == 100
    assert body["summary"]["mae"] == 100


def test_accuracy(db):
    seed(db)
    body = client.get("/api/accuracy").json()
    assert body["summary"]["count"] == 144
    assert body["summary"]["bias"] == 100
    assert len(body["by_hour"]) == 24
    assert len(body["daily"]) == 3

    one_day = client.get("/api/accuracy", params={"start": "2026-01-02", "end": "2026-01-02"}).json()
    assert one_day["summary"]["count"] == 48


def test_decision_hour_is_validated(db):
    assert client.get("/api/meta", params={"decision_hour": 30}).status_code == 422
