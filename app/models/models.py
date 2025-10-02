from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel


class Portfolio(Base, BaseModel):
    __tablename__ = "portfolios"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    base_currency = Column(String(3), nullable=False)
    benchmark_id = Column(UUID(as_uuid=True), ForeignKey("benchmarks.id"), nullable=True)
    
    # Relationships
    user = relationship("User", backref="portfolios")
    benchmark = relationship("Benchmark")


class Account(Base, BaseModel):
    __tablename__ = "accounts"

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    broker = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # broker nebo cash
    currency = Column(String(3), nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", backref="accounts")


class Asset(Base, BaseModel):
    __tablename__ = "assets"

    symbol = Column(String(50), unique=True, nullable=False)
    isin = Column(String(12), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # stock, etf, bond, crypto, fund, cash
    sector = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    currency = Column(String(3), nullable=False)


class Transaction(Base, BaseModel):
    __tablename__ = "transactions"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # BUY, SELL, DIVIDEND, FEE, TAX, SPLIT, FX
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    fee = Column(Numeric(20, 8), nullable=False, default=0)
    tax = Column(Numeric(20, 8), nullable=False, default=0)
    gross_amount = Column(Numeric(20, 8), nullable=False)
    trade_currency = Column(String(3), nullable=False)
    fx_rate_to_portfolio = Column(Numeric(20, 8), nullable=False)
    trade_time = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String, nullable=True)
    
    # Relationships
    account = relationship("Account", backref="transactions")
    asset = relationship("Asset")


class Dividend(Base, BaseModel):
    __tablename__ = "dividends"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    ex_date = Column(DateTime(timezone=True), nullable=False)
    pay_date = Column(DateTime(timezone=True), nullable=False)
    gross_amount = Column(Numeric(20, 8), nullable=False)
    withholding_tax = Column(Numeric(20, 8), nullable=False)
    net_amount = Column(Numeric(20, 8), nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Relationships
    account = relationship("Account", backref="dividends")
    asset = relationship("Asset")


class Price(Base):
    __tablename__ = "prices"

    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    close = Column(Numeric(20, 8), nullable=False)
    currency = Column(String(3), nullable=False)
    source = Column(String(50), nullable=False)
    
    # Relationships
    asset = relationship("Asset", backref="prices")


class Benchmark(Base, BaseModel):
    __tablename__ = "benchmarks"

    symbol = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False)


class ReportCache(Base, BaseModel):
    __tablename__ = "report_cache"

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(255), nullable=False)
    payload = Column(JSONB, nullable=False)
    computed_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", backref="report_cache")


class AuditLog(Base, BaseModel):
    __tablename__ = "audit_log"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)
    before = Column(JSONB, nullable=True)
    after = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", backref="audit_logs")