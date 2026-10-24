import { useCallback } from "react";
import { mw, signedMw } from "../format";
import Chart, { baseOption } from "./Chart";

const barStyle = (color) => ({ color, borderRadius: [4, 4, 0, 0] });

export function DailyChart({ data }) {
  const build = useCallback(
    (theme) => {
      const base = baseOption(theme);
      return {
        ...base,
        legend: { ...base.legend, data: ["Average error", "Bias"] },
        tooltip: { ...base.tooltip, valueFormatter: mw },
        xAxis: { ...base.xAxis, type: "category", data: data.map((d) => d.day.slice(5)) },
        yAxis: { ...base.yAxis, type: "value", name: "MW", nameGap: 12 },
        series: [
          { name: "Average error", type: "bar", data: data.map((d) => d.mae), barMaxWidth: 18, itemStyle: barStyle(theme.forecast) },
          { name: "Bias", type: "line", data: data.map((d) => d.bias), showSymbol: false, lineStyle: { width: 2, color: theme.actual }, itemStyle: { color: theme.actual } },
        ],
      };
    },
    [data]
  );
  return <Chart build={build} label="Average forecast error and bias for each delivery day" />;
}

export function HourChart({ data }) {
  const build = useCallback(
    (theme) => {
      const base = baseOption(theme);
      return {
        ...base,
        legend: { ...base.legend, data: ["Average error", "Bias"] },
        tooltip: { ...base.tooltip, valueFormatter: mw },
        xAxis: { ...base.xAxis, type: "category", data: data.map((d) => `${String(d.hour).padStart(2, "0")}:00`), axisLabel: { ...base.xAxis.axisLabel, interval: 2 } },
        yAxis: { ...base.yAxis, type: "value", name: "MW", nameGap: 12 },
        series: [
          { name: "Average error", type: "bar", data: data.map((d) => d.mae), barMaxWidth: 18, itemStyle: barStyle(theme.forecast) },
          { name: "Bias", type: "line", data: data.map((d) => d.bias), showSymbol: false, lineStyle: { width: 2, color: theme.actual }, itemStyle: { color: theme.actual } },
        ],
      };
    },
    [data]
  );
  return <Chart build={build} label="Average forecast error and bias by hour of the delivery day" />;
}

export function HistogramChart({ data }) {
  const build = useCallback(
    (theme) => {
      const base = baseOption(theme);
      return {
        ...base,
        legend: { show: false },
        tooltip: {
          ...base.tooltip,
          formatter: (p) => {
            const d = data[p[0].dataIndex];
            return `${signedMw(d.lower)} to ${signedMw(d.upper)}<br/><b>${d.count}</b> half hours`;
          },
        },
        xAxis: {
          ...base.xAxis,
          type: "category",
          data: data.map((d) => String((d.lower + d.upper) / 2)),
          name: "Forecast minus actual (MW)",
          nameLocation: "middle",
          nameGap: 28,
        },
        yAxis: { ...base.yAxis, type: "value", name: "Half hours", nameGap: 12 },
        grid: { ...base.grid, top: 40, bottom: 52 },
        series: [
          {
            type: "bar",
            data: data.map((d) => d.count),
            barCategoryGap: "8%",
            itemStyle: barStyle(theme.forecast),
          },
        ],
      };
    },
    [data]
  );
  return <Chart build={build} label="How often forecasts were too high or too low, by size of error" />;
}
