import { useEffect, useState } from "react";
import { useStore } from "../store";

export default function TradeHistory() {
  const trades = useStore((s) => s.trades);
  const fetchTrades = useStore((s) => s.fetchTrades);
  const updateNotes = useStore((s) => s.updateNotes);
  const exportCsv = useStore((s) => s.exportCsv);
  const filterSymbol = useStore((s) => s.filterSymbol);
  const filterSide = useStore((s) => s.filterSide);
  const setFilter = useStore((s) => s.setFilter);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editNote, setEditNote] = useState("");

  useEffect(() => { fetchTrades(); }, []);

  const handleSaveNote = async (id: number) => {
    await updateNotes(id, editNote);
    setEditingId(null);
  };

  return (
    <section className="trade-history">
      <div className="section-header">
        <h2>📋 Trade History</h2>
        <div className="history-filters">
          <input
            placeholder="Filter symbol…"
            value={filterSymbol}
            onChange={(e) => { setFilter("filterSymbol", e.target.value); fetchTrades(); }}
          />
          <select value={filterSide} onChange={(e) => { setFilter("filterSide", e.target.value); fetchTrades(); }}>
            <option value="">All Sides</option>
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <button onClick={exportCsv} className="btn-export">⬇ Export CSV</button>
        </div>
      </div>

      {trades.length === 0 ? (
        <p className="empty">No trades yet. Execute your first order!</p>
      ) : (
        <div className="table-wrapper">
          <table className="trade-table">
            <thead>
              <tr>
                <th>#</th><th>Symbol</th><th>Side</th><th>Qty</th>
                <th>Price</th><th>P&amp;L</th><th>Status</th><th>Time</th><th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((t) => (
                <tr key={t.id} className={t.side === "buy" ? "row-buy" : "row-sell"}>
                  <td>{t.id}</td>
                  <td><b>{t.symbol}</b></td>
                  <td className={t.side === "buy" ? "bull" : "bear"}>{t.side.toUpperCase()}</td>
                  <td>{t.quantity}</td>
                  <td>${t.price.toFixed(2)}</td>
                  <td className={t.pnl != null ? (t.pnl >= 0 ? "profit" : "loss") : ""}>
                    {t.pnl != null ? `$${t.pnl.toFixed(2)}` : "—"}
                  </td>
                  <td><span className={`status-badge ${t.status}`}>{t.status}</span></td>
                  <td>{new Date(t.created_at).toLocaleString()}</td>
                  <td>
                    {editingId === t.id ? (
                      <span className="note-edit">
                        <input
                          value={editNote}
                          onChange={(e) => setEditNote(e.target.value)}
                          autoFocus
                        />
                        <button onClick={() => handleSaveNote(t.id)}>✓</button>
                        <button onClick={() => setEditingId(null)}>✕</button>
                      </span>
                    ) : (
                      <span
                        className="note-cell"
                        onClick={() => { setEditingId(t.id); setEditNote(t.notes ?? ""); }}
                        title="Click to edit"
                      >
                        {t.notes || <em>add note…</em>}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
