from datetime import date, datetime

from pydantic import BaseModel


class Meta(BaseModel):
    decision_hour: int
    first_day: date | None
    last_day: date | None


class ForecastPoint(BaseModel):
    time: datetime
    forecast: float
    actual: float | None
    publish_time: datetime


class DaySummary(BaseModel):
    forecast_mwh: float
    actual_mwh: float | None
    peak_forecast_mw: float
    peak_time: datetime
    min_forecast_mw: float
    avg_forecast_mw: float
    first_publish_time: datetime
    last_publish_time: datetime
    mae: float | None


class DayForecast(BaseModel):
    day: date
    decision_time: datetime
    band_mw: float | None
    summary: DaySummary
    points: list[ForecastPoint]


class Summary(BaseModel):
    count: int
    mean_actual: float
    mean_forecast: float
    bias: float
    mae: float
    rmse: float
    wape: float | None
    p50_abs: float
    p90_abs: float
    p95_abs: float
    shortfall_p95: float
    surplus_p95: float


class HourStat(BaseModel):
    hour: int
    mae: float
    bias: float
    count: int


class DayStat(BaseModel):
    day: date
    mae: float
    bias: float
    mean_actual: float
    count: int


class Bin(BaseModel):
    lower: float
    upper: float
    count: int


class Accuracy(BaseModel):
    start: date
    end: date
    decision_hour: int
    summary: Summary
    by_hour: list[HourStat]
    daily: list[DayStat]
    histogram: list[Bin]
