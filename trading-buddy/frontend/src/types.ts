export type SignalType =
  | "RSI_OVERSOLD"
  | "RSI_OVERBOUGHT"
  | "MA_CROSSOVER_BULL"
  | "MA_CROSSOVER_BEAR"
  | "BREAKOUT_UP"
  | "BREAKOUT_DOWN";

export interface Signal {
  id: string;
  symbol: string;
  signal_type: SignalType;
  strength: number;
  price: number;
  suggested_side: "buy" | "sell";
  timestamp: string;
}

export interface Trade {
  id: number;
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  price: number;
  order_type: string;
  status: string;
  signal_id: string | null;
  pnl: number | null;
  notes: string | null;
  created_at: string;
  filled_at: string | null;
}

export interface Analytics {
  total_trades: number;
  win_rate: number | null;
  avg_pnl: number | null;
  best_trade: number | null;
  worst_trade: number | null;
  total_pnl: number | null;
  by_signal_type: Record<string, { count: number; total_pnl: number }>;
}

export interface TickMessage {
  type: "tick";
  symbol: string;
  price: number;
  signals: Signal[];
}
