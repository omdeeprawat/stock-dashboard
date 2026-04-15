import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from "recharts";
import { fetchCompanies, fetchStockData, fetchSummary } from "./api";
import type { Company, StockDataPoint, Summary, TimeRange } from "./types";
import "./App.css";

const TIME_RANGES: { label: string; value: TimeRange }[] = [
  { label: "30D", value: 30 },
  { label: "90D", value: 90 },
  { label: "180D", value: 180 },
  { label: "1Y", value: 365 },
];

const fmt = (n: number) =>
  n.toLocaleString("en-IN", { maximumFractionDigits: 2 });

type TooltipItem = {
  dataKey: string;
  color: string;
  name: string;
  value: number;
};

type CustomTooltipProps = {
  active?: boolean;
  payload?: TooltipItem[];
  label?: string;
};

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#161c1e", border: "1px solid #1f2d2f",
      padding: "10px 14px", borderRadius: 6, fontFamily: "Inter, sans-serif", fontSize: 11
    }}>
      <p style={{ color: "#6b8a88", marginBottom: 6 }}>{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: ₹{fmt(p.value)}
        </p>
      ))}
    </div>
  );
};

export default function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selected, setSelected] = useState<Company | null>(null);
  const [stockData, setStockData] = useState<StockDataPoint[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCompanies().then(setCompanies);
  }, []);

  useEffect(() => {
    if (!selected) return;
    Promise.all([
      fetchStockData(selected.symbol, timeRange),
      fetchSummary(selected.symbol),
    ]).then(([data, sum]) => {
      setStockData(data);
      setSummary(sum);
    }).catch(() => {
      setStockData([]);
      setSummary(null);
    }).finally(() => {
      setLoading(false);
    });
  }, [selected, timeRange]);

  const chartData = stockData.map((d) => ({
    date: d.date.slice(5),       // show MM-DD
    Close: +d.close.toFixed(2),
    "7D MA": d.ma_7 ? +d.ma_7.toFixed(2) : null,
  }));

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <span className="header-logo">StockIQ</span>
        <div className="header-divider" />
        <span className="header-subtitle">MARKET INTELLIGENCE DASHBOARD</span>
        <div className="header-dot" />
      </header>

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-label">Markets</div>
        {companies.map((c) => (
          <div
            key={c.symbol}
            className={`company-item ${selected?.symbol === c.symbol ? "active" : ""}`}
            onClick={() => {
              setLoading(true);
              setSelected(c);
            }}
          >
            <span className="company-symbol">{c.symbol.replace(".NS", "")}</span>
            <span className="company-name">{c.name}</span>
            <span className="company-sector">{c.sector}</span>
          </div>
        ))}
      </aside>

      {/* Main */}
      <main className="main">
        {!selected ? (
          <div className="empty-state">
            <div className="empty-state-icon">📈</div>
            <h3>SELECT A COMPANY</h3>
            <p>Choose a stock from the sidebar to view its data</p>
          </div>
        ) : (
          <>
            {/* Stock Header */}
            <div className="stock-header">
              <div className="stock-title">
                <h2>{selected.symbol.replace(".NS", "")}</h2>
                <p>{selected.name} · {selected.sector}</p>
              </div>
              <div className="time-filters">
                {TIME_RANGES.map((t) => (
                  <button
                    key={t.value}
                    className={`filter-btn ${timeRange === t.value ? "active" : ""}`}
                    onClick={() => {
                      setLoading(true);
                      setTimeRange(t.value);
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Summary Cards */}
            {summary && (
              <div className="summary-grid">
                <div className="summary-card">
                  <div className="summary-card-label">52W High</div>
                  <div className="summary-card-value green">₹{fmt(summary.high_52w)}</div>
                </div>
                <div className="summary-card">
                  <div className="summary-card-label">52W Low</div>
                  <div className="summary-card-value red">₹{fmt(summary.low_52w)}</div>
                </div>
                <div className="summary-card">
                  <div className="summary-card-label">Avg Close</div>
                  <div className="summary-card-value">₹{fmt(summary.avg_close)}</div>
                </div>
                <div className="summary-card">
                  <div className="summary-card-label">Volatility Score</div>
                  <div className={`summary-card-value ${summary.volatility_score > 0.3 ? "red" : "green"}`}>
                    {(summary.volatility_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* Chart */}
            <div className="chart-card">
              <div className="chart-card-header">
                <span className="chart-title">Closing Price + 7-Day Moving Average</span>
                <div className="chart-legend">
                  <span><span className="legend-dot" style={{ background: "#00c896" }} />Close</span>
                  <span><span className="legend-dot" style={{ background: "#4a9eff" }} />7D MA</span>
                </div>
              </div>
              {loading ? (
                <div className="loading">LOADING</div>
              ) : (
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2d2f" />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: "#3d5452", fontSize: 10, fontFamily: "Inter" }}
                      tickLine={false}
                      axisLine={{ stroke: "#1f2d2f" }}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fill: "#3d5452", fontSize: 10, fontFamily: "Inter" }}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(v) => `₹${v}`}
                      width={70}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Line
                      type="monotone"
                      dataKey="Close"
                      stroke="#00c896"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, fill: "#00c896" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="7D MA"
                      stroke="#4a9eff"
                      strokeWidth={1.5}
                      dot={false}
                      strokeDasharray="4 4"
                      connectNulls
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}