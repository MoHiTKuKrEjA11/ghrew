import { useEffect, useState } from "react";
import { getMeta } from "./api/client";
import Accuracy from "./pages/Accuracy";
import Overview from "./pages/Overview";

const TABS = [
  { id: "forecast", label: "Day-ahead forecast" },
  { id: "accuracy", label: "Forecast accuracy" },
];
const HOURS = [6, 7, 8, 9, 10, 11, 12];

export default function App() {
  const [tab, setTab] = useState("forecast");
  const [decisionHour, setDecisionHour] = useState(9);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMeta(decisionHour).then(setMeta).catch((e) => setError(e.message));
  }, [decisionHour]);

  return (
    <div className="page">
      <header>
        <div>
          <h1>Wind forecast monitor</h1>
          <p>GB wind generation for day-ahead buying</p>
        </div>
        <label className="decision">
          Buying decision made at
          <select value={decisionHour} onChange={(e) => setDecisionHour(Number(e.target.value))}>
            {HOURS.map((h) => (
              <option key={h} value={h}>
                {String(h).padStart(2, "0")}:00 UTC, day before
              </option>
            ))}
          </select>
        </label>
      </header>

      <nav aria-label="Pages">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? "active" : ""} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </nav>

      <main>
        {error && <p className="notice error">Could not reach the server: {error}</p>}
        {tab === "forecast" ? (
          <Overview meta={meta} decisionHour={decisionHour} />
        ) : (
          <Accuracy meta={meta} decisionHour={decisionHour} />
        )}
      </main>

      <footer>Source: Elexon BMRS (FUELHH actuals, WINDFOR forecasts). Times are UTC.</footer>
    </div>
  );
}
