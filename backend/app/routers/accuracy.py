from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Accuracy
from ..services import metrics
from ..services.forecast_selector import day_ahead_points
from .forecast import HourParam

router = APIRouter(prefix="/api")


@router.get("/accuracy", response_model=Accuracy)
def accuracy(
    start: date | None = None,
    end: date | None = None,
    decision_hour: int = HourParam,
    db: Session = Depends(get_db),
):
    points = day_ahead_points(db, decision_hour)
    if not points:
        raise HTTPException(404, "No data loaded. Run `python -m app.loader` first.")

    start = start or points[0].time.date()
    end = end or points[-1].time.date()
    selected = [p for p in points if start <= p.time.date() <= end]

    summary = metrics.summarize(selected)
    if summary is None:
        raise HTTPException(404, "No forecast/actual pairs in that range")

    return {
        "start": start,
        "end": end,
        "decision_hour": decision_hour,
        "summary": summary,
        "by_hour": metrics.by_hour(selected),
        "daily": metrics.daily(selected),
        "histogram": metrics.histogram(selected),
    }
