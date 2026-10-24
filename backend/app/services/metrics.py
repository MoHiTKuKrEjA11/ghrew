from collections import defaultdict
from math import sqrt

from .forecast_selector import Point

HISTOGRAM_BIN_MW = 500


def percentile(values: list[float], q: float) -> float:
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def paired(points: list[Point]) -> list[Point]:
    return [p for p in points if p.actual is not None]


def summarize(points: list[Point]) -> dict | None:
    pts = paired(points)
    if not pts:
        return None
    errors = [p.error for p in pts]
    abs_errors = [abs(e) for e in errors]
    n = len(pts)
    total_actual = sum(p.actual for p in pts)
    return {
        "count": n,
        "mean_actual": total_actual / n,
        "mean_forecast": sum(p.forecast for p in pts) / n,
        "bias": sum(errors) / n,
        "mae": sum(abs_errors) / n,
        "rmse": sqrt(sum(e * e for e in errors) / n),
        "wape": 100 * sum(abs_errors) / total_actual if total_actual else None,
        "p50_abs": percentile(abs_errors, 0.5),
        "p90_abs": percentile(abs_errors, 0.9),
        "p95_abs": percentile(abs_errors, 0.95),
        # How far wind came in below / above forecast in the worst 5% of half hours.
        "shortfall_p95": max(0.0, percentile(errors, 0.95)),
        "surplus_p95": max(0.0, percentile([-e for e in errors], 0.95)),
    }


def by_hour(points: list[Point]) -> list[dict]:
    groups = defaultdict(list)
    for p in paired(points):
        groups[p.time.hour].append(p.error)
    return [
        {
            "hour": h,
            "mae": sum(abs(e) for e in errs) / len(errs),
            "bias": sum(errs) / len(errs),
            "count": len(errs),
        }
        for h, errs in sorted(groups.items())
    ]


def daily(points: list[Point]) -> list[dict]:
    groups = defaultdict(list)
    for p in paired(points):
        groups[p.time.date()].append(p)
    out = []
    for day, pts in sorted(groups.items()):
        errs = [p.error for p in pts]
        out.append(
            {
                "day": day,
                "mae": sum(abs(e) for e in errs) / len(errs),
                "bias": sum(errs) / len(errs),
                "mean_actual": sum(p.actual for p in pts) / len(pts),
                "count": len(pts),
            }
        )
    return out


def histogram(points: list[Point]) -> list[dict]:
    errors = [p.error for p in paired(points)]
    if not errors:
        return []
    w = HISTOGRAM_BIN_MW
    first = int(min(errors) // w)
    last = int(max(errors) // w)
    counts = defaultdict(int)
    for e in errors:
        counts[int(e // w)] += 1
    return [{"lower": b * w, "upper": (b + 1) * w, "count": counts[b]} for b in range(first, last + 1)]
