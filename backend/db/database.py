from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime,
    JSON, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("symbol", "date", name="uq_signal_symbol_date"),)

    id           = Column(Integer, primary_key=True)
    symbol       = Column(String, nullable=False)
    date         = Column(Date, nullable=False)
    score        = Column(Float, nullable=False)
    signal_label = Column(String, nullable=False)
    trade_type   = Column(String, nullable=False)
    entry_price  = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)
    stop_loss    = Column(Float, nullable=True)
    risk_reward  = Column(Float, nullable=True)
    indicators   = Column(JSON, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    result = relationship("Result", back_populates="signal", uselist=False)


class Result(Base):
    __tablename__ = "results"

    id           = Column(Integer, primary_key=True)
    signal_id    = Column(Integer, ForeignKey("signals.id"), unique=True)
    symbol       = Column(String, nullable=False)
    date         = Column(Date, nullable=False)
    entry_price  = Column(Float, nullable=True)
    high_of_day  = Column(Float, nullable=True)
    low_of_day   = Column(Float, nullable=True)
    close_price  = Column(Float, nullable=True)
    result_pct   = Column(Float, nullable=True)
    status       = Column(String, nullable=False)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    signal = relationship("Signal", back_populates="result")


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def get_session() -> Session:
    return Session(engine)


def init_db() -> None:
    Base.metadata.create_all(engine)
