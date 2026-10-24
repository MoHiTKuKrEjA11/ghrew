import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, MarkLineComponent, TooltipComponent } from "echarts/components";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { useEffect, useRef, useState } from "react";

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, MarkLineComponent, TooltipComponent, CanvasRenderer]);

const FONT = "IBM Plex Sans, system-ui, sans-serif";

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

export const readTheme = () => ({
  forecast: css("--forecast"),
  actual: css("--actual"),
  ink: css("--ink"),
  muted: css("--muted"),
  grid: css("--grid"),
  surface: css("--surface"),
});

export function baseOption(theme) {
  const axis = {
    axisLine: { lineStyle: { color: theme.grid } },
    axisTick: { show: false },
    axisLabel: { color: theme.muted, fontFamily: FONT },
    nameTextStyle: { color: theme.muted, fontFamily: FONT },
  };
  return {
    textStyle: { fontFamily: FONT },
    animationDuration: 300,
    grid: { left: 64, right: 24, top: 64, bottom: 36 },
    legend: { top: 0, left: 0, icon: "roundRect", itemWidth: 14, itemHeight: 4, textStyle: { color: theme.ink } },
    tooltip: {
      trigger: "axis",
      backgroundColor: theme.surface,
      borderColor: theme.grid,
      textStyle: { color: theme.ink, fontFamily: FONT, fontSize: 13 },
    },
    xAxis: { ...axis },
    yAxis: { ...axis, splitLine: { lineStyle: { color: theme.grid } }, axisLine: { show: false } },
  };
}

/** `build(theme)` returns an ECharts option. The chart re-renders when the colour scheme changes. */
export default function Chart({ build, height = 340, label }) {
  const el = useRef(null);
  const chart = useRef(null);
  const [scheme, setScheme] = useState(0);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setScheme((n) => n + 1);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    chart.current = echarts.init(el.current);
    const onResize = () => chart.current.resize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.current.dispose();
    };
  }, []);

  useEffect(() => {
    chart.current.setOption(build(readTheme()), true);
  }, [build, scheme]);

  return <div ref={el} style={{ height }} role="img" aria-label={label} />;
}
