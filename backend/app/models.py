from datetime import datetime

from sqlalchemy import DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Actual(Base):
    __tablename__ = "actuals"

    start_time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    generation: Mapped[float] = mapped_column(Float)


class Forecast(Base):
    __tablename__ = "forecasts"

    start_time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    publish_time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    generation: Mapped[float] = mapped_column(Float)
