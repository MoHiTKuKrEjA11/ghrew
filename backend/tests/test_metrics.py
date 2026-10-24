from datetime import datetime

import pytest

from app.services import metrics
from app.services.forecast_selector import Point

PUB = datetime(2026, 1, 1, 9)


def point(hour, forecast, actual):
    return Point(datetime(2026, 1, 2, hour), forecast, PUB, actual)


POINTS = [point(0, 110, 100), point(1, 90, 100), point(2, 130, 100), point(3, 100, None)]


def test_summary_values():
    s = metrics.summarize(POINTS)
    assert s["count"] == 3  # the point without an actual is ignored
    assert s["bias"] == pytest.approx(10)  # errors are +10, -10, +30
    assert s["mae"] == pytest.approx(50 / 3)
    assert s["rmse"] == pytest.approx((1100 / 3) ** 0.5)
    assert s["wape"] == pytest.approx(100 * 50 / 300)


def test_percentile():
    assert metrics.percentile([1, 2, 3, 4, 5], 0.5) == 3
    assert metrics.percentile([0, 10], 0.9) == pytest.approx(9)


def test_summary_empty():
    assert metrics.summarize([point(0, 100, None)]) is None


def test_by_hour_and_daily():
    hours = metrics.by_hour(POINTS)
    assert [h["hour"] for h in hours] == [0, 1, 2]
    assert hours[2]["bias"] == 30
    (day,) = metrics.daily(POINTS)
    assert day["count"] == 3


def test_histogram_counts_every_pair():
    bins = metrics.histogram(POINTS)
    assert sum(b["count"] for b in bins) == 3
