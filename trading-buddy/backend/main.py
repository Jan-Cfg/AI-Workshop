"""Trading Buddy – FastAPI application entry point."""
import asyncio
import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, get_db
from market_data import register, unregister, market_feed_loop, SYMBOLS, get_price_history
from trade_service import place_order, get_trades, get_analytics, update_trade_notes, update_pnl
from signal_engine import compute_signals

app = FastAPI(title="Trading Buddy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(market_feed_loop())


# ── Schemas ───────────────────────────────────────────────────────────────────

class OrderRequest(BaseModel):
    symbol: str
    side: str          # "buy" | "sell"
    quantity: float
    price: float
    order_type: str = "market"
    signal_id: Optional[str] = None
    notes: Optional[str] = None


class NotesUpdate(BaseModel):
    notes: str


class PnlUpdate(BaseModel):
    pnl: float


# ── Market data ───────────────────────────────────────────────────────────────

@app.get("/symbols")
def list_symbols():
    return {"symbols": SYMBOLS}


@app.get("/signals/{symbol}")
def get_signals(symbol: str):
    """Return current signals for a symbol based on its price history."""
    history = get_price_history(symbol.upper())
    if not history:
        return {"signals": []}
    import dataclasses
    signals = compute_signals(symbol.upper(), history)
    return {"signals": [dataclasses.asdict(s) for s in signals]}


# ── Orders ────────────────────────────────────────────────────────────────────

@app.post("/orders", status_code=201)
def create_order(req: OrderRequest, db: Session = Depends(get_db)):
    if req.side not in ("buy", "sell"):
        raise HTTPException(400, "side must be 'buy' or 'sell'")
    if req.quantity <= 0:
        raise HTTPException(400, "quantity must be positive")
    trade = place_order(
        db,
        symbol=req.symbol.upper(),
        side=req.side,
        quantity=req.quantity,
        price=req.price,
        order_type=req.order_type,
        signal_id=req.signal_id,
        notes=req.notes,
    )
    return _trade_dict(trade)


# ── Trade history ─────────────────────────────────────────────────────────────

@app.get("/trades")
def list_trades(
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    trades = get_trades(db, symbol=symbol, side=side, limit=limit, offset=offset)
    return {"trades": [_trade_dict(t) for t in trades]}


@app.patch("/trades/{trade_id}/notes")
def patch_notes(trade_id: int, body: NotesUpdate, db: Session = Depends(get_db)):
    trade = update_trade_notes(db, trade_id, body.notes)
    if not trade:
        raise HTTPException(404, "Trade not found")
    return _trade_dict(trade)


@app.patch("/trades/{trade_id}/pnl")
def patch_pnl(trade_id: int, body: PnlUpdate, db: Session = Depends(get_db)):
    trade = update_pnl(db, trade_id, body.pnl)
    if not trade:
        raise HTTPException(404, "Trade not found")
    return _trade_dict(trade)


@app.get("/trades/export/csv")
def export_trades_csv(db: Session = Depends(get_db)):
    trades = get_trades(db, limit=10000)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "symbol", "side", "quantity", "price", "order_type",
        "status", "signal_id", "pnl", "notes", "created_at", "filled_at",
    ])
    writer.writeheader()
    for t in trades:
        writer.writerow(_trade_dict(t))
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trades.csv"},
    )


# ── Analytics ─────────────────────────────────────────────────────────────────

@app.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    return get_analytics(db)


# ── WebSocket feed ────────────────────────────────────────────────────────────

@app.websocket("/ws/market")
async def market_ws(websocket: WebSocket):
    await websocket.accept()
    await register(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep-alive ping
    except WebSocketDisconnect:
        pass
    finally:
        await unregister(websocket)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _trade_dict(trade) -> dict:
    return {
        "id": trade.id,
        "symbol": trade.symbol,
        "side": trade.side,
        "quantity": trade.quantity,
        "price": trade.price,
        "order_type": trade.order_type,
        "status": trade.status,
        "signal_id": trade.signal_id,
        "pnl": trade.pnl,
        "notes": trade.notes,
        "created_at": trade.created_at.isoformat() if trade.created_at else None,
        "filled_at": trade.filled_at.isoformat() if trade.filled_at else None,
    }
