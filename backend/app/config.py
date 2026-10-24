from datetime import date

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./wind.db"
    cors_origins: str = "http://localhost:5173"
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"

    # Day-ahead decisions are made on D-1 at this hour (UTC, same as UK time in January).
    decision_hour: int = 9
    # Range of days on which purchase decisions are made.
    decision_from: date = date(2026, 1, 1)
    decision_to: date = date(2026, 1, 31)


settings = Settings()
