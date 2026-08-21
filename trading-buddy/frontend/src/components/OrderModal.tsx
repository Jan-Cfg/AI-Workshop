import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

export default function OrderModal() {
  const pendingOrder = useStore((s) => s.pendingOrder);
  const closeOrder = useStore((s) => s.closeOrder);
  const submitOrder = useStore((s) => s.submitOrder);

  const [quantity, setQuantity] = useState("1");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (pendingOrder) {
      setQuantity("1");
      setNotes("");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [pendingOrder]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeOrder();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [closeOrder]);

  if (!pendingOrder) return null;

  const isBuy = pendingOrder.suggested_side === "buy";
  const total = (parseFloat(quantity) || 0) * (pendingOrder.price ?? 0);

  const handleSubmit = async () => {
    const qty = parseFloat(quantity);
    if (!qty || qty <= 0) return;
    setSubmitting(true);
    await submitOrder(qty, notes);
    setSubmitting(false);
  };

  return (
    <div className="modal-backdrop" onClick={closeOrder}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{isBuy ? "🟢 Buy Order" : "🔴 Sell Order"}</h3>

        <table className="order-details">
          <tbody>
            <tr><td>Symbol</td><td><b>{pendingOrder.symbol}</b></td></tr>
            <tr><td>Side</td><td><b className={isBuy ? "bull" : "bear"}>{pendingOrder.suggested_side?.toUpperCase()}</b></td></tr>
            <tr><td>Price</td><td><b>${pendingOrder.price?.toFixed(2)}</b></td></tr>
            <tr><td>Signal</td><td>{pendingOrder.signal_type}</td></tr>
          </tbody>
        </table>

        <label>
          Quantity
          <input
            ref={inputRef}
            type="number"
            min="0.0001"
            step="0.0001"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </label>

        <div className="total-line">
          Total ≈ <b>${total.toFixed(2)}</b>
        </div>

        <label>
          Journal note (optional)
          <textarea
            rows={2}
            placeholder="Why are you taking this trade?"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>

        <div className="modal-actions">
          <button className="btn-cancel" onClick={closeOrder}>Cancel [Esc]</button>
          <button
            className={`btn-confirm ${isBuy ? "buy" : "sell"}`}
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? "Submitting…" : `Confirm ${isBuy ? "Buy" : "Sell"}`}
          </button>
        </div>
      </div>
    </div>
  );
}
