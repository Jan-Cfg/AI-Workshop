import { create } from "zustand";
import type { Signal, Trade, Analytics, TickMessage } from "./types";

const API = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws/market";

interface AppState {
  // Market
  prices: Record<string, number>;
  signals: Signal[];
  // Filters
  filterSymbol: string;
  filterSide: string;
  filterMinStrength: number;
  // Orders
  pendingOrder: Partial<Signal> | null;
  // Trades
  trades: Trade[];
  analytics: Analytics | null;
  // Actions
  setFilter: (key: "filterSymbol" | "filterSide" | "filterMinStrength", value: string | number) => void;
  openOrder: (signal: Signal) => void;
  closeOrder: () => void;
  submitOrder: (quantity: number, notes: string) => Promise<void>;
  fetchTrades: () => Promise<void>;
  fetchAnalytics: () => Promise<void>;
  updateNotes: (id: number, notes: string) => Promise<void>;
  exportCsv: () => void;
  connectWs: () => void;
}

export const useStore = create<AppState>((set, get) => ({
  prices: {},
  signals: [],
  filterSymbol: "",
  filterSide: "",
  filterMinStrength: 0,
  pendingOrder: null,
  trades: [],
  analytics: null,

  setFilter: (key, value) => set({ [key]: value }),

  openOrder: (signal) => set({ pendingOrder: signal }),
  closeOrder: () => set({ pendingOrder: null }),

  submitOrder: async (quantity, notes) => {
    const order = get().pendingOrder as Signal;
    if (!order) return;
    await fetch(`${API}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: order.symbol,
        side: order.suggested_side,
        quantity,
        price: order.price,
        signal_id: order.id,
        notes: notes || null,
      }),
    });
    set({ pendingOrder: null });
    get().fetchTrades();
  },

  fetchTrades: async () => {
    const symbol = get().filterSymbol;
    const side = get().filterSide;
    const params = new URLSearchParams();
    if (symbol) params.set("symbol", symbol);
    if (side) params.set("side", side);
    const res = await fetch(`${API}/trades?${params}`);
    const data = await res.json();
    set({ trades: data.trades });
  },

  fetchAnalytics: async () => {
    const res = await fetch(`${API}/analytics`);
    set({ analytics: await res.json() });
  },

  updateNotes: async (id, notes) => {
    await fetch(`${API}/trades/${id}/notes`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notes }),
    });
    get().fetchTrades();
  },

  exportCsv: () => {
    window.open(`${API}/trades/export/csv`, "_blank");
  },

  connectWs: () => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (e) => {
      const msg: TickMessage = JSON.parse(e.data);
      if (msg.type === "tick") {
        set((state) => ({
          prices: { ...state.prices, [msg.symbol]: msg.price },
          signals: [
            ...state.signals.filter((s) => s.symbol !== msg.symbol),
            ...msg.signals,
          ],
        }));
      }
    };
    ws.onclose = () => setTimeout(() => get().connectWs(), 2000);
  },
}));
