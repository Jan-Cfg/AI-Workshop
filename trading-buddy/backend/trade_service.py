"""Trade execution + persistence layer."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models import Trade


def place_order(
    db: Session,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    order_type: str = "market",
    signal_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Trade:
    """Persist a new trade and simulate broker fill."""
    trade = Trade(
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        order_type=order_type,
        status="filled",          # simulated instant fill
        signal_id=signal_id,
        notes=notes,
        created_at=datetime.utcnow(),
        filled_at=datetime.utcnow(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def update_trade_notes(db: Session, trade_id: int, notes: str) -> Optional[Trade]:
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if trade:
        trade.notes = notes
        db.commit()
        db.refresh(trade)
    return trade


def update_pnl(db: Session, trade_id: int, pnl: float) -> Optional[Trade]:
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if trade:
        trade.pnl = pnl
        db.commit()
        db.refresh(trade)
    return trade


def get_trades(
    db: Session,
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[Trade]:
    q = db.query(Trade)
    if symbol:
        q = q.filter(Trade.symbol == symbol.upper())
    if side:
        q = q.filter(Trade.side == side.lower())
    return q.order_by(Trade.created_at.desc()).offset(offset).limit(limit).all()


def get_analytics(db: Session) -> dict:
    trades = db.query(Trade).filter(Trade.status == "filled").all()
    if not trades:
        return {"total_trades": 0}

    pnl_values = [t.pnl for t in trades if t.pnl is not None]
    wins = [p for p in pnl_values if p > 0]
    losses = [p for p in pnl_values if p <= 0]

    by_signal: dict = {}
    for t in trades:
        key = t.signal_id or "manual"
        by_signal.setdefault(key, {"count": 0, "total_pnl": 0.0})
        by_signal[key]["count"] += 1
        if t.pnl:
            by_signal[key]["total_pnl"] += t.pnl

    return {
        "total_trades": len(trades),
        "win_rate": round(len(wins) / len(pnl_values), 3) if pnl_values else None,
        "avg_pnl": round(sum(pnl_values) / len(pnl_values), 4) if pnl_values else None,
        "best_trade": max(pnl_values) if pnl_values else None,
        "worst_trade": min(pnl_values) if pnl_values else None,
        "total_pnl": round(sum(pnl_values), 4) if pnl_values else None,
        "by_signal_type": by_signal,
    }
