import { useEffect } from "react";
import { useStore } from "../store";
import type { Signal } from "../types";

const SIGNAL_LABELS: Record<string, string> = {
  RSI_OVERSOLD: "RSI Oversold",
  RSI_OVERBOUGHT: "RSI Overbought",
  MA_CROSSOVER_BULL: "MA Crossover ↑",
  MA_CROSSOVER_BEAR: "MA Crossover ↓",
  BREAKOUT_UP: "Breakout ↑",
  BREAKOUT_DOWN: "Breakout ↓",
};

export default function SignalPanel() {
  const signals = useStore((s) => s.signals);
  const prices = useStore((s) => s.prices);
  const filterSymbol = useStore((s) => s.filterSymbol);
  const filterSide = useStore((s) => s.filterSide);
  const filterMinStrength = useStore((s) => s.filterMinStrength);
  const setFilter = useStore((s) => s.setFilter);
  const openOrder = useStore((s) => s.openOrder);

  const filtered = signals.filter((s) => {
    if (filterSymbol && s.symbol !== filterSymbol) return false;
    if (filterSide && s.suggested_side !== filterSide) return false;
    if (s.strength < filterMinStrength) return false;
    return true;
  });

  // Hotkeys: B = quick-buy first buy signal, S = quick-sell first sell signal
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "INPUT" || (e.target as HTMLElement).tagName === "TEXTAREA") return;
      if (e.key === "b" || e.key === "B") {
        const sig = filtered.find((s) => s.suggested_side === "buy");
        if (sig) openOrder(sig);
      }
      if (e.key === "s" || e.key === "S") {
        const sig = filtered.find((s) => s.suggested_side === "sell");
        if (sig) openOrder(sig);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [filtered, openOrder]);

  return (
    <section className="signal-panel">
      <h2>📡 Live Signals</h2>

      <div className="filters">
        <select value={filterSymbol} onChange={(e) => setFilter("filterSymbol", e.target.value)}>
          <option value="">All Symbols</option>
          {Array.from(new Set(signals.map((s) => s.symbol))).map((sym) => (
            <option key={sym}>{sym}</option>
          ))}
        </select>
        <select value={filterSide} onChange={(e) => setFilter("filterSide", e.target.value)}>
          <option value="">All Sides</option>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
        <label className="strength-filter">
          Min Strength:
          <input
            type="range" min={0} max={1} step={0.05}
            value={filterMinStrength}
            onChange={(e) => setFilter("filterMinStrength", parseFloat(e.target.value))}
          />
          <span>{Math.round(filterMinStrength * 100)}%</span>
        </label>
        <small className="hotkey-hint">Hotkeys: [B] quick-buy · [S] quick-sell</small>
      </div>

      {filtered.length === 0 && <p className="empty">No active signals — watching the market…</p>}
      <div className="signal-cards">
        {filtered.map((sig) => (
          <SignalCard
            key={sig.id}
            signal={sig}
            currentPrice={prices[sig.symbol]}
            onExecute={openOrder}
          />
        ))}
      </div>
    </section>
  );
}

function SignalCard({
  signal,
  currentPrice,
  onExecute,
}: {
  signal: Signal;
  currentPrice?: number;
  onExecute: (s: Signal) => void;
}) {
  const isBuy = signal.suggested_side === "buy";
  return (
    <div className={`signal-card ${isBuy ? "bull" : "bear"}`}>
      <div className="card-header">
        <strong>{signal.symbol}</strong>
        <span className="badge">{SIGNAL_LABELS[signal.signal_type] ?? signal.signal_type}</span>
      </div>
      <div className="card-body">
        <span>Price: <b>${(currentPrice ?? signal.price).toFixed(2)}</b></span>
        <span>Strength: <b>{Math.round(signal.strength * 100)}%</b></span>
        <span className="ts">{new Date(signal.timestamp).toLocaleTimeString()}</span>
      </div>
      <button className={`execute-btn ${isBuy ? "buy" : "sell"}`} onClick={() => onExecute(signal)}>
        {isBuy ? "🟢 BUY" : "🔴 SELL"}
      </button>
    </div>
  );
}
