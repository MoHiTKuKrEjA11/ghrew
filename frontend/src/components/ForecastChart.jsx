import { useCallback } from "react";
import { mw, utcTime } from "../format";
import Chart, { baseOption } from "./Chart";

export default function ForecastChart({ data }) {
  const build = useCallback(
    (theme) => {
      const times = data.points.map((p) => utcTime(p.time));
      const hasActual = data.points.some((p) => p.actual != null);
      const base = baseOption(theme);
      const band = data.band_mw;

      const series = [
        {
          name: "Forecast",
          type: "line",
          data: data.points.map((p) => p.forecast),
          showSymbol: false,
          lineStyle: { width: 2, color: theme.forecast },
          itemStyle: { color: theme.forecast },
        },
      ];
      if (hasActual) {
        series.push({
          name: "Actual",
          type: "line",
          data: data.points.map((p) => p.actual),
          showSymbol: false,
          lineStyle: { width: 2, color: theme.actual },
          itemStyle: { color: theme.actual },
        });
      }
      if (band != null) {
        const lower = data.points.map((p) => Math.max(0, p.forecast - band));
        const spread = data.points.map((p, i) => p.forecast + band - lower[i]);
        series.push(
          { name: "Lower", type: "line", data: lower, stack: "band", symbol: "none", lineStyle: { opacity: 0 }, tooltip: { show: false } },
          {
            name: "Typical error range",
            type: "line",
            data: spread,
            stack: "band",
            symbol: "none",
            lineStyle: { opacity: 0 },
            areaStyle: { color: theme.forecast, opacity: 0.12 },
            itemStyle: { color: theme.forecast },
            tooltip: { show: false },
          }
        );
      }

      return {
        ...base,
        legend: { ...base.legend, data: series.map((s) => s.name).filter((n) => n !== "Lower") },
        tooltip: {
          ...base.tooltip,
          formatter: (params) => {
            const rows = params
              .filter((p) => p.seriesName === "Forecast" || p.seriesName === "Actual")
              .map((p) => `${p.marker} ${p.seriesName}: <b>${mw(p.value)}</b>`);
            return `${params[0].axisValue} UTC<br/>${rows.join("<br/>")}`;
          },
        },
        xAxis: { ...base.xAxis, type: "category", data: times, boundaryGap: false, axisLabel: { ...base.xAxis.axisLabel, interval: 5 } },
        yAxis: { ...base.yAxis, type: "value", name: "MW", nameGap: 12, min: 0 },
        series,
      };
    },
    [data]
  );

  return <Chart build={build} height={380} label="Forecast and actual wind generation for the selected day" />;
}
