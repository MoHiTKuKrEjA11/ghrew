import time
from datetime import date, datetime, timedelta, timezone

import httpx

from .config import settings


def parse_time(value: str) -> datetime:
    """ISO string from Elexon -> naive UTC datetime."""
    return datetime.fromisoformat(value).astimezone(timezone.utc).replace(tzinfo=None)


def _get(client: httpx.Client, path: str, params: dict) -> list[dict]:
    url = f"{settings.elexon_base_url}{path}"
    for attempt in range(5):
        resp = client.get(url, params=params, headers={"Accept": "application/json"})
        if resp.status_code == 429:
            time.sleep(2 * (attempt + 1))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Elexon rate limit not clearing for {path}")


def fetch_actuals(client: httpx.Client, start: date, end: date) -> dict[datetime, float]:
    """Actual wind generation (MW) keyed by half-hour start time. `end` is inclusive."""
    out: dict[datetime, float] = {}
    day = start
    while day <= end:
        chunk_end = min(day + timedelta(days=6), end)
        rows = _get(
            client,
            "/datasets/FUELHH/stream",
            {
                "settlementDateFrom": day.isoformat(),
                "settlementDateTo": chunk_end.isoformat(),
                "fuelType": ["WIND"],
            },
        )
        for r in rows:
            if r.get("fuelType") == "WIND" and r.get("generation") is not None:
                out[parse_time(r["startTime"])] = float(r["generation"])
        day = chunk_end + timedelta(days=1)
    return out


def fetch_forecasts(
    client: httpx.Client, publish_from: datetime, publish_to: datetime
) -> dict[tuple[datetime, datetime], float]:
    """Wind forecasts (MW) keyed by (start_time, publish_time). Fetched one day of publishes at a time."""
    out: dict[tuple[datetime, datetime], float] = {}
    cur = publish_from
    while cur < publish_to:
        nxt = min(cur + timedelta(days=1), publish_to)
        rows = _get(
            client,
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": cur.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        for r in rows:
            if r.get("generation") is not None:
                out[(parse_time(r["startTime"]), parse_time(r["publishTime"]))] = float(r["generation"])
        cur = nxt
    return out
