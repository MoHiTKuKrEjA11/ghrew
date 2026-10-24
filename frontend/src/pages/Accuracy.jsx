import { useEffect, useState } from "react";
import { getAccuracy } from "../api/client";
import { DailyChart, HistogramChart, HourChart } from "../components/AccuracyCharts";
import Stats from "../components/Stats";
import { mw, pct } from "../format";

export default function Accuracy({ meta, decisionHour }) {
  const [range, setRange] = useState({ start: "", end: "" });
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getAccuracy(decisionHour, range.start, range.end)
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && (setData(null), setError(e.message)));
    return () => {
      cancelled = true;
    };
  }, [decisionHour, range]);

  const set = (key) => (e) => setRange((r) => ({ ...r, [key]: e.target.value }));
  const s = data?.summary;

  return (
    <>
      <div className="filters">
        <label>
          From
          <input type="date" value={range.start} min={meta?.first_day} max={meta?.last_day} onChange={set("start")} />
        </label>
        <label>
          To
          <input type="date" value={range.end} min={meta?.first_day} max={meta?.last_day} onChange={set("end")} />
        </label>
        {(range.start || range.end) && <button onClick={() => setRange({ start: "", end: "" })}>Show all days</button>}
      </div>

      {error && <p className="notice error">{error}</p>}

      {data && (
        <>
          <h2>How wrong were the forecasts?</h2>
          <p className="lede">
            Each half hour is compared with the forecast you would have had at decision time. Error means forecast minus
            actual, so a positive number means the forecast was too high.
          </p>

          <Stats
            items={[
              { label: "Average error", value: mw(s.mae), note: `${pct(s.wape)} of average wind output` },
              {
                label: "Bias",
                value: `${s.bias > 0 ? "+" : ""}${Math.round(s.bias)} MW`,
                note: s.bias > 0 ? "Forecasts ran too high" : "Forecasts ran too low",
              },
              { label: "9 in 10 within", value: mw(s.p90_abs), note: `Half of all errors are under ${mw(s.p50_abs)}` },
              {
                label: "Worst-case shortfall",
                value: mw(s.shortfall_p95),
                note: `Wind came in this far below forecast in 1 in 20 half hours`,
              },
            ]}
          />

          <section>
            <h3>Error by delivery day</h3>
            <p className="caption">Bars show the average size of the miss. The line shows its direction.</p>
            <DailyChart data={data.daily} />
          </section>

          <section>
            <h3>Error by hour of the day</h3>
            <p className="caption">Which hours of the day are hardest to forecast (times in UTC).</p>
            <HourChart data={data.by_hour} />
          </section>

          <section>
            <h3>How big the misses were</h3>
            <p className="caption">
              Left of zero, wind beat the forecast. Right of zero, wind fell short of it and extra power had to be bought.
            </p>
            <HistogramChart data={data.histogram} />
          </section>
        </>
      )}
    </>
  );
}
