from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Actual, Forecast


@dataclass
class Point:
    time: datetime
    forecast: float
    publish_time: datetime
    actual: float | None

    @property
    def error(self) -> float | None:
        """Forecast minus actual. Positive means the forecast was too high."""
        return None if self.actual is None else self.forecast - self.actual


_cache: dict[int, list[Point]] = {}


def clear_cache() -> None:
    _cache.clear()


def decision_time(day: date, hour: int) -> datetime:
    """When the day-ahead purchase for delivery `day` is made: the day before, at `hour` (UTC)."""
    return datetime.combine(day - timedelta(days=1), time(hour))


def day_ahead_points(db: Session, hour: int) -> list[Point]:
    """For every half hour, the latest forecast published before that day's decision time."""
    if hour in _cache:
        return _cache[hour]

    forecasts = db.execute(
        select(Forecast.start_time, Forecast.publish_time, Forecast.generation).order_by(
            Forecast.start_time, Forecast.publish_time
        )
    ).all()
    actuals = dict(db.execute(select(Actual.start_time, Actual.generation)).all())

    chosen: dict[datetime, tuple[datetime, float]] = {}
    for start, published, generation in forecasts:
        if published <= decision_time(start.date(), hour):
            chosen[start] = (published, generation)  # rows are sorted, so the last one wins

    points = [
        Point(start, generation, published, actuals.get(start))
        for start, (published, generation) in sorted(chosen.items())
    ]
    _cache[hour] = points
    return points
