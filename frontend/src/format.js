const num = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

export const mw = (v) => (v == null ? "–" : `${num.format(v)} MW`);
export const mwh = (v) => (v == null ? "–" : `${num.format(v)} MWh`);
export const gwh = (v) => (v == null ? "–" : `${(v / 1000).toFixed(1)} GWh`);
export const signedMw = (v) => (v == null ? "–" : `${v > 0 ? "+" : ""}${num.format(v)} MW`);
export const pct = (v) => (v == null ? "–" : `${v.toFixed(1)}%`);

const dateTime = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "UTC",
});
export const utcDateTime = (iso) => `${dateTime.format(new Date(iso))} UTC`;

const hhmm = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" });
export const utcTime = (iso) => hhmm.format(new Date(iso));

const dayLabel = new Intl.DateTimeFormat("en-GB", {
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
export const longDay = (isoDay) => dayLabel.format(new Date(`${isoDay}T00:00:00Z`));

export const shiftDay = (isoDay, delta) => {
  const d = new Date(`${isoDay}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + delta);
  return d.toISOString().slice(0, 10);
};
