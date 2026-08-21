import { useEffect } from "react";
import { useStore } from "../store";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const COLORS = ["#22c55e", "#ef4444", "#3b82f6", "#f59e0b", "#8b5cf6", "#06b6d4"];

export default function AnalyticsDashboard() {
  const analytics = useStore((s) => s.analytics);
  const fetchAnalytics = useStore((s) => s.fetchAnalytics);

  useEffect(() => { fetchAnalytics(); }, []);

  if (!analytics) return <p className="empty">Loading analytics…</p>;
  if (analytics.total_trades === 0) return <p className="empty">No trade data yet.</p>;

  const signalData = Object.entries(analytics.by_signal_type ?? {}).map(([key, val]) => ({
    name: key.replace(/_/g, " "),
    count: val.count,
    pnl: parseFloat(val.total_pnl.toFixed(2)),
  }));

  const pieData = [
    { name: "Wins", value: analytics.win_rate != null ? Math.round(analytics.win_rate * analytics.total_trades) : 0 },
    { name: "Losses", value: analytics.win_rate != null ? analytics.total_trades - Math.round(analytics.win_rate * analytics.total_trades) : 0 },
  ];

  return (
    <section className="analytics">
      <h2>📊 Analytics</h2>

      <div className="stat-cards">
        <StatCard label="Total Trades" value={analytics.total_trades} />
        <StatCard label="Win Rate" value={analytics.win_rate != null ? `${(analytics.win_rate * 100).toFixed(1)}%` : "—"} />
        <StatCard label="Avg P&L" value={analytics.avg_pnl != null ? `$${analytics.avg_pnl.toFixed(2)}` : "—"} color={analytics.avg_pnl != null && analytics.avg_pnl >= 0 ? "profit" : "loss"} />
        <StatCard label="Total P&L" value={analytics.total_pnl != null ? `$${analytics.total_pnl.toFixed(2)}` : "—"} color={analytics.total_pnl != null && analytics.total_pnl >= 0 ? "profit" : "loss"} />
        <StatCard label="Best Trade" value={analytics.best_trade != null ? `$${analytics.best_trade.toFixed(2)}` : "—"} color="profit" />
        <StatCard label="Worst Trade" value={analytics.worst_trade != null ? `$${analytics.worst_trade.toFixed(2)}` : "—"} color="loss" />
      </div>

      <div className="charts-row">
        <div className="chart-box">
          <h4>Trades by Signal Type</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={signalData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-box">
          <h4>Win / Loss</h4>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="stat-card">
      <span className="stat-label">{label}</span>
      <span className={`stat-value ${color ?? ""}`}>{value}</span>
    </div>
  );
}
