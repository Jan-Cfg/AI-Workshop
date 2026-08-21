"""Market data simulator + WebSocket broadcaster.

In production swap `_simulate_tick` with a real feed (Alpaca, Binance, etc.).
"""
import asyncio
import random
import math
from collections import defaultdict
from typing import Dict, List, Set
from fastapi import WebSocket

# Price history per symbol (rolling 100 ticks)
_price_history: Dict[str, List[float]] = defaultdict(list)
_MAX_HISTORY = 100

# Connected WebSocket clients
_clients: Set[WebSocket] = set()

SYMBOLS = ["AAPL", "TSLA", "BTC/USD", "ETH/USD", "MSFT", "NVDA"]

# Seed starting prices
_last_price: Dict[str, float] = {
    "AAPL": 185.0, "TSLA": 250.0, "BTC/USD": 62000.0,
    "ETH/USD": 3200.0, "MSFT": 420.0, "NVDA": 880.0,
}


def _simulate_tick(symbol: str) -> float:
    """Return the next simulated price with realistic random walk."""
    last = _last_price[symbol]
    change_pct = random.gauss(0, 0.003)          # 0.3 % std dev per tick
    new_price = round(last * (1 + change_pct), 4)
    _last_price[symbol] = new_price
    return new_price


def get_price_history(symbol: str) -> List[float]:
    return list(_price_history[symbol])


async def register(ws: WebSocket):
    _clients.add(ws)


async def unregister(ws: WebSocket):
    _clients.discard(ws)


async def broadcast(message: dict):
    import json
    dead = set()
    for ws in _clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    _clients -= dead


async def market_feed_loop():
    """Background task: tick every second, compute signals, broadcast."""
    from signal_engine import compute_signals
    import dataclasses

    while True:
        for symbol in SYMBOLS:
            price = _simulate_tick(symbol)
            history = _price_history[symbol]
            history.append(price)
            if len(history) > _MAX_HISTORY:
                history.pop(0)

            signals = compute_signals(symbol, history)
            tick_payload = {
                "type": "tick",
                "symbol": symbol,
                "price": price,
                "signals": [dataclasses.asdict(s) for s in signals],
            }
            await broadcast(tick_payload)

        await asyncio.sleep(1)
