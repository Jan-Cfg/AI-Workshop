import { useEffect, useState } from "react";
import { useStore } from "./store";
import SignalPanel from "./components/SignalPanel";
import OrderModal from "./components/OrderModal";
import TradeHistory from "./components/TradeHistory";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import "./App.css";

type Tab = "signals" | "history" | "analytics";

export default function App() {
  const connectWs = useStore((s) => s.connectWs);
  const prices = useStore((s) => s.prices);
  const [tab, setTab] = useState<Tab>("signals");

  useEffect(() => { connectWs(); }, []);

  return (
    <div className="app">
      <header className="app-header">
        <span className="logo">📈 Trading Buddy</span>
        <div className="ticker-bar">
          {Object.entries(prices).map(([sym, price]) => (
            <span key={sym} className="ticker-item">
              {sym} <b>${price.toFixed(2)}</b>
            </span>
          ))}
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === "signals" ? "active" : ""} onClick={() => setTab("signals")}>Signals</button>
        <button className={tab === "history" ? "active" : ""} onClick={() => setTab("history")}>Trade History</button>
        <button className={tab === "analytics" ? "active" : ""} onClick={() => setTab("analytics")}>Analytics</button>
      </nav>

      <main className="app-body">
        {tab === "signals" && <SignalPanel />}
        {tab === "history" && <TradeHistory />}
        {tab === "analytics" && <AnalyticsDashboard />}
      </main>

      <OrderModal />
    </div>
  );
}
