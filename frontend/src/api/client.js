const BASE = import.meta.env.VITE_API_URL || "";

async function get(path, params = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
  const res = await fetch(`${BASE}/api${path}?${query}`);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const getMeta = (decisionHour) => get("/meta", { decision_hour: decisionHour });
export const getDayForecast = (day, decisionHour) =>
  get("/forecast", { day, decision_hour: decisionHour });
export const getAccuracy = (decisionHour, start, end) =>
  get("/accuracy", { decision_hour: decisionHour, start, end });
