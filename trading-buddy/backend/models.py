"""SQLAlchemy models for Trading Buddy."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(4), nullable=False)          # "buy" | "sell"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    order_type = Column(String(10), default="market") # "market" | "limit"
    status = Column(String(12), default="submitted")  # submitted | filled | rejected
    signal_id = Column(String(64), nullable=True)     # link to triggering signal
    pnl = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)
