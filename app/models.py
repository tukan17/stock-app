from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    auth_provider = Column(String, nullable=False, default="password")
    two_factor_enabled = Column(Boolean, default=False)

    portfolios = relationship("Portfolio", back_populates="owner", cascade="all,delete")


class Benchmark(Base, TimestampMixin):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=True)
    custom_series_ref = Column(String, nullable=True)
    name = Column(String, nullable=False)
    currency = Column(String(3), nullable=False)

    portfolios = relationship("Portfolio", back_populates="benchmark")


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    base_currency = Column(String(3), nullable=False, default="USD")
    benchmark_id = Column(Integer, ForeignKey("benchmarks.id"), nullable=True)

    owner = relationship("User", back_populates="portfolios")
    benchmark = relationship("Benchmark", back_populates="portfolios")
    accounts = relationship("Account", back_populates="portfolio", cascade="all,delete")
    report_caches = relationship(
        "ReportCache", back_populates="portfolio", cascade="all,delete-orphan"
    )


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    broker = Column(String, nullable=False)
    account_name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="broker")
    currency = Column(String(3), nullable=False)

    portfolio = relationship("Portfolio", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all,delete-orphan"
    )
    dividends = relationship(
        "Dividend", back_populates="account", cascade="all,delete-orphan"
    )


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    sector = Column(String, nullable=True)
    region = Column(String, nullable=True)
    currency = Column(String(3), nullable=False)

    transactions = relationship(
        "Transaction", back_populates="asset", cascade="all,delete-orphan"
    )
    dividends = relationship("Dividend", back_populates="asset", cascade="all,delete")
    prices = relationship("Price", back_populates="asset", cascade="all,delete")


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "trade_time",
            "asset_id",
            "qty",
            "price",
            name="uq_transaction_dedup",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    type = Column(String, nullable=False)
    qty = Column(Numeric(18, 4), nullable=False)
    price = Column(Numeric(18, 4), nullable=False)
    fee = Column(Numeric(18, 4), nullable=True, default=0)
    tax = Column(Numeric(18, 4), nullable=True, default=0)
    gross_amount = Column(Numeric(18, 4), nullable=True)
    trade_currency = Column(String(3), nullable=False)
    fx_rate_to_portfolio_ccy = Column(Float, nullable=True)
    trade_time = Column(DateTime, default=datetime.utcnow, index=True)

    account = relationship("Account", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")


class Dividend(Base, TimestampMixin):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    ex_date = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    gross = Column(Numeric(18, 4), nullable=False)
    withholding_tax = Column(Numeric(18, 4), nullable=True, default=0)
    net = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), nullable=False)

    account = relationship("Account", back_populates="dividends")
    asset = relationship("Asset", back_populates="dividends")


class Price(Base, TimestampMixin):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("asset_id", "date", name="uq_price_asset_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    close = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    source = Column(String, nullable=True)

    asset = relationship("Asset", back_populates="prices")


class ReportCache(Base, TimestampMixin):
    __tablename__ = "report_cache"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "key", name="uq_report_cache_portfolio_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    key = Column(String, nullable=False)
    payload_json = Column(String, nullable=False)
    computed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="report_caches")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    before = Column(String, nullable=True)
    after = Column(String, nullable=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
