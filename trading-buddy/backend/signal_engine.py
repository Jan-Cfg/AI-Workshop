"""Signal engine – RSI, moving-average crossover, and breakout detectors."""
import uuid
import math
from dataclasses import dataclass, field
from typing import Literal, List, Dict


SignalType = Literal["RSI_OVERSOLD", "RSI_OVERBOUGHT", "MA_CROSSOVER_BULL", "MA_CROSSOVER_BEAR", "BREAKOUT_UP", "BREAKOUT_DOWN"]


@dataclass
class Signal:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    signal_type: SignalType = "RSI_OVERSOLD"
    strength: float = 0.0          # 0–1
    price: float = 0.0
    suggested_side: str = "buy"    # "buy" | "sell"
    timestamp: str = ""


def _ema(prices: List[float], period: int) -> List[float]:
    k = 2 / (period + 1)
    result = [prices[0]]
    for p in prices[1:]:
        result.append(p * k + result[-1] * (1 - k))
    return result


def _rsi(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d for d in deltas[-period:] if d > 0]
    losses = [-d for d in deltas[-period:] if d < 0]
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 1e-9
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_signals(symbol: str, prices: List[float]) -> List[Signal]:
    """Return a list of active signals for *symbol* given its price history."""
    from datetime import datetime, timezone

    signals: List[Signal] = []
    now = datetime.now(timezone.utc).isoformat()

    if len(prices) < 2:
        return signals

    current_price = prices[-1]

    # ── RSI ──────────────────────────────────────────────────────────────────
    rsi = _rsi(prices)
    if rsi < 30:
        signals.append(Signal(
            symbol=symbol, signal_type="RSI_OVERSOLD",
            strength=round((30 - rsi) / 30, 3),
            price=current_price, suggested_side="buy", timestamp=now,
        ))
    elif rsi > 70:
        signals.append(Signal(
            symbol=symbol, signal_type="RSI_OVERBOUGHT",
            strength=round((rsi - 70) / 30, 3),
            price=current_price, suggested_side="sell", timestamp=now,
        ))

    # ── Moving-average crossover (fast=9, slow=21) ────────────────────────
    if len(prices) >= 21:
        fast = _ema(prices, 9)
        slow = _ema(prices, 21)
        if fast[-1] > slow[-1] and fast[-2] <= slow[-2]:
            gap = (fast[-1] - slow[-1]) / slow[-1]
            signals.append(Signal(
                symbol=symbol, signal_type="MA_CROSSOVER_BULL",
                strength=round(min(gap * 100, 1.0), 3),
                price=current_price, suggested_side="buy", timestamp=now,
            ))
        elif fast[-1] < slow[-1] and fast[-2] >= slow[-2]:
            gap = (slow[-1] - fast[-1]) / slow[-1]
            signals.append(Signal(
                symbol=symbol, signal_type="MA_CROSSOVER_BEAR",
                strength=round(min(gap * 100, 1.0), 3),
                price=current_price, suggested_side="sell", timestamp=now,
            ))

    # ── Breakout (price breaks 20-period high/low) ────────────────────────
    if len(prices) >= 21:
        window = prices[-21:-1]
        high20 = max(window)
        low20 = min(window)
        if current_price > high20:
            signals.append(Signal(
                symbol=symbol, signal_type="BREAKOUT_UP",
                strength=round(min((current_price - high20) / high20 * 100, 1.0), 3),
                price=current_price, suggested_side="buy", timestamp=now,
            ))
        elif current_price < low20:
            signals.append(Signal(
                symbol=symbol, signal_type="BREAKOUT_DOWN",
                strength=round(min((low20 - current_price) / low20 * 100, 1.0), 3),
                price=current_price, suggested_side="sell", timestamp=now,
            ))

    return signals
