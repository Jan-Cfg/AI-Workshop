# Trading Buddy

A full-stack trading assistant with real-time signal detection, one-click order execution, and trade history.

## Stack
| Layer | Tech |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Zustand + Recharts |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Realtime | WebSocket (market feed) |

---

## Quick Start

### 1. Backend
```bash
cd trading-buddy/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 2. Frontend
```bash
cd trading-buddy/frontend
npm install
npm run dev
```
App: http://localhost:5173

---

## Features

### 📡 Opportunity Identification
- Live WebSocket market feed (simulated; swap `_simulate_tick` in `market_data.py` for a real broker feed)
- Signal engine: **RSI** (oversold/overbought), **MA crossover** (9/21 EMA), **Breakout** (20-period high/low)
- Dashboard with live signal cards showing symbol, type, price, and strength
- Filters by symbol, side (buy/sell), and minimum signal strength

### ⚡ Fast Order Execution
- **One-click BUY / SELL** button on every signal card
- **Keyboard shortcuts**: `B` = quick-buy, `S` = quick-sell (first matching signal)
- Confirmation modal pre-filled with signal details — dismiss with `Esc`
- Optional journal note before submitting
- Order persisted and status shown instantly

### 📋 Trade History & Future Reference
- Full trade log: symbol, side, qty, price, status, P&L, signal link, timestamp
- Inline journal notes (click any note cell to edit)
- Filter by symbol and side
- Export to CSV
- **Analytics Dashboard**: win rate, average P&L, best/worst trade, total P&L
- Charts: trades by signal type (bar), win/loss ratio (pie)

---

## API Reference

| Method | Path | Description |
|---|---|---|
| GET | `/symbols` | List tracked symbols |
| GET | `/signals/{symbol}` | Current signals for a symbol |
| POST | `/orders` | Place an order |
| GET | `/trades` | Trade history (filterable) |
| PATCH | `/trades/{id}/notes` | Update trade journal note |
| PATCH | `/trades/{id}/pnl` | Update P&L |
| GET | `/trades/export/csv` | Download trades as CSV |
| GET | `/analytics` | Aggregated stats |
| WS | `/ws/market` | Real-time price + signal feed |

---

## Connecting a Real Broker

Replace the `_simulate_tick` function in `backend/market_data.py` with a real WebSocket feed (e.g. Alpaca, Binance). Update `place_order` in `trade_service.py` to call your broker's order API before persisting the trade.
