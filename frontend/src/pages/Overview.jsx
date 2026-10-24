import { useEffect, useState } from "react";
import { getDayForecast } from "../api/client";
import ForecastChart from "../components/ForecastChart";
import Stats from "../components/Stats";
import { gwh, longDay, mw, shiftDay, utcDateTime, utcTime } from "../format";

export default function Overview({ meta, decisionHour }) {
  const [day, setDay] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (meta?.first_day && !day) setDay(meta.first_day);
  }, [meta, day]);

  useEffect(() => {
    if (!day) return;
    let cancelled = false;
    setError(null);
    getDayForecast(day, decisionHour)
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && (setData(null), setError(e.message)));
    return () => {
      cancelled = true;
    };
  }, [day, decisionHour]);

  if (!meta?.first_day) return <p className="notice">No data loaded yet. Run the data loader (see README).</p>;

  const s = data?.summary;
  return (
    <>
      <div className="filters">
        <label>
          Delivery day
          <div className="day-picker">
            <button onClick={() => setDay(shiftDay(day, -1))} disabled={day <= meta.first_day} aria-label="Previous day">
              ‹
            </button>
            <input
              type="date"
              value={day || ""}
              min={meta.first_day}
              max={meta.last_day}
              onChange={(e) => e.target.value && setDay(e.target.value)}
            />
            <button onClick={() => setDay(shiftDay(day, 1))} disabled={day >= meta.last_day} aria-label="Next day">
              ›
            </button>
          </div>
        </label>
      </div>

      {error && <p className="notice error">{error}</p>}

      {data && (
        <>
          <h2>{longDay(data.day)}</h2>
          <p className="lede">
            Forecast available when buying for this day: the latest one published before{" "}
            <strong>{utcDateTime(data.decision_time)}</strong>. The newest of these was published at{" "}
            {utcDateTime(s.last_publish_time)}.
          </p>

          <Stats
            items={[
              { label: "Expected wind energy", value: gwh(s.forecast_mwh), note: `Average ${mw(s.avg_forecast_mw)}` },
              { label: "Highest forecast", value: mw(s.peak_forecast_mw), note: `At ${utcTime(s.peak_time)} UTC` },
              { label: "Lowest forecast", value: mw(s.min_forecast_mw) },
              s.actual_mwh != null
                ? { label: "What actually happened", value: gwh(s.actual_mwh), note: `Average miss ${mw(s.mae)}` }
                : { label: "What actually happened", value: "–", note: "No actuals yet" },
            ]}
          />

          <section>
            <ForecastChart data={data} />
            {data.band_mw != null && (
              <p className="caption">
                Shaded band: forecast ± {mw(data.band_mw)}. Over the whole period, 9 in 10 half hours landed within
                that distance of the forecast.
              </p>
            )}
          </section>
        </>
      )}
    </>
  );
}
