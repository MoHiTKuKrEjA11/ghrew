from datetime import datetime

from app.models import Actual, Forecast
from app.services.forecast_selector import day_ahead_points

TARGET = datetime(2026, 1, 2, 0, 0)


def test_picks_latest_forecast_before_cutoff(db):
    db.add_all(
        [
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 8, 0), generation=100),
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 8, 59), generation=200),
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 9, 0), generation=300),
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 10, 0), generation=400),
            Actual(start_time=TARGET, generation=250),
        ]
    )
    db.commit()

    (point,) = day_ahead_points(db, 9)
    assert point.forecast == 300
    assert point.publish_time == datetime(2026, 1, 1, 9, 0)
    assert point.actual == 250
    assert point.error == 50


def test_skips_target_with_no_forecast_before_cutoff(db):
    db.add(Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 12, 0), generation=100))
    db.commit()
    assert day_ahead_points(db, 9) == []


def test_later_decision_hour_sees_newer_forecast(db):
    db.add_all(
        [
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 8, 0), generation=100),
            Forecast(start_time=TARGET, publish_time=datetime(2026, 1, 1, 12, 0), generation=500),
        ]
    )
    db.commit()
    assert day_ahead_points(db, 9)[0].forecast == 100
    assert day_ahead_points(db, 13)[0].forecast == 500
