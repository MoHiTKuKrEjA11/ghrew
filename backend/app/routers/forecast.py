from datetime import date, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas import DayForecast, Meta
from ..services import metrics
from ..services.forecast_selector import day_ahead_points, decision_time

router = APIRouter(prefix="/api")

HourParam = Query(settings.decision_hour, ge=0, le=23, description="Decision hour (UTC) on the day before delivery")


def utc(dt):
    return dt.replace(tzinfo=timezone.utc)


@router.get("/meta", response_model=Meta)
def meta(decision_hour: int = HourParam, db: Session = Depends(get_db)):
    points = day_ahead_points(db, decision_hour)
    return Meta(
        decision_hour=decision_hour,
        first_day=points[0].time.date() if points else None,
        last_day=points[-1].time.date() if points else None,
    )


@router.get("/forecast", response_model=DayForecast)
def day_forecast(day: date, decision_hour: int = HourParam, db: Session = Depends(get_db)):
    points = [p for p in day_ahead_points(db, decision_hour) if p.time.date() == day]
    if not points:
        raise HTTPException(404, f"No forecast available for {day}")

    overall = metrics.summarize(day_ahead_points(db, decision_hour))
    day_stats = metrics.summarize(points)
    peak = max(points, key=lambda p: p.forecast)
    actuals = [p.actual for p in points if p.actual is not None]
    forecasts = [p.forecast for p in points]

    return {
        "day": day,
        "decision_time": utc(decision_time(day, decision_hour)),
        "band_mw": overall["p90_abs"] if overall else None,
        "summary": {
            "forecast_mwh": sum(forecasts) * 0.5,
            "actual_mwh": sum(actuals) * 0.5 if len(actuals) == len(points) else None,
            "peak_forecast_mw": peak.forecast,
            "peak_time": utc(peak.time),
            "min_forecast_mw": min(forecasts),
            "avg_forecast_mw": sum(forecasts) / len(forecasts),
            "first_publish_time": utc(min(p.publish_time for p in points)),
            "last_publish_time": utc(max(p.publish_time for p in points)),
            "mae": day_stats["mae"] if day_stats else None,
        },
        "points": [
            {
                "time": utc(p.time),
                "forecast": p.forecast,
                "actual": p.actual,
                "publish_time": utc(p.publish_time),
            }
            for p in points
        ],
    }
