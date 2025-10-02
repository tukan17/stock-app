from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, condecimal


Decimal = condecimal(max_digits=18, decimal_places=4)


class PortfolioBase(BaseModel):
    name: str
    base_currency: str = Field(..., min_length=3, max_length=3)
    benchmark_id: Optional[int] = None


class PortfolioCreate(PortfolioBase):
    user_id: int


class PortfolioUpdate(BaseModel):
    name: Optional[str]
    base_currency: Optional[str]
    benchmark_id: Optional[int]


class Portfolio(PortfolioBase):
    id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    portfolio_id: int
    broker: str
    account_name: str
    type: str = Field(..., regex="^(broker|cash)$")
    currency: str = Field(..., min_length=3, max_length=3)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    broker: Optional[str]
    account_name: Optional[str]
    type: Optional[str]
    currency: Optional[str]


class Account(AccountBase):
    id: int

    class Config:
        orm_mode = True


class AssetBase(BaseModel):
    symbol: str
    isin: Optional[str]
    name: str
    type: str
    sector: Optional[str]
    region: Optional[str]
    currency: str = Field(..., min_length=3, max_length=3)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    symbol: Optional[str]
    isin: Optional[str]
    name: Optional[str]
    type: Optional[str]
    sector: Optional[str]
    region: Optional[str]
    currency: Optional[str]


class Asset(AssetBase):
    id: int

    class Config:
        orm_mode = True


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    FEE = "FEE"
    TAX = "TAX"
    SPLIT = "SPLIT"
    FX = "FX"


class TransactionBase(BaseModel):
    account_id: int
    asset_id: int
    type: TransactionType
    qty: Decimal
    price: Decimal
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    gross_amount: Optional[Decimal]
    trade_currency: str = Field(..., min_length=3, max_length=3)
    fx_rate_to_portfolio_ccy: Optional[float]
    trade_time: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType]
    qty: Optional[Decimal]
    price: Optional[Decimal]
    fee: Optional[Decimal]
    tax: Optional[Decimal]
    gross_amount: Optional[Decimal]
    trade_currency: Optional[str]
    fx_rate_to_portfolio_ccy: Optional[float]
    trade_time: Optional[datetime]


class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True


class DividendBase(BaseModel):
    account_id: int
    asset_id: int
    ex_date: date
    pay_date: date
    gross: Decimal
    withholding_tax: Optional[Decimal] = 0
    net: Decimal
    currency: str = Field(..., min_length=3, max_length=3)


class DividendCreate(DividendBase):
    pass


class DividendUpdate(BaseModel):
    ex_date: Optional[date]
    pay_date: Optional[date]
    gross: Optional[Decimal]
    withholding_tax: Optional[Decimal]
    net: Optional[Decimal]
    currency: Optional[str]


class Dividend(DividendBase):
    id: int

    class Config:
        orm_mode = True


class PriceBase(BaseModel):
    asset_id: int
    date: date
    close: Decimal
    currency: str = Field(..., min_length=3, max_length=3)
    source: Optional[str]


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    close: Optional[Decimal]
    currency: Optional[str]
    source: Optional[str]


class Price(PriceBase):
    id: int

    class Config:
        orm_mode = True


class BenchmarkBase(BaseModel):
    symbol: Optional[str]
    custom_series_ref: Optional[str]
    name: str
    currency: str = Field(..., min_length=3, max_length=3)


class BenchmarkCreate(BenchmarkBase):
    pass


class BenchmarkUpdate(BaseModel):
    symbol: Optional[str]
    custom_series_ref: Optional[str]
    name: Optional[str]
    currency: Optional[str]


class Benchmark(BenchmarkBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    auth_provider: str = "password"
    two_factor_enabled: bool = False


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[str]
    auth_provider: Optional[str]
    two_factor_enabled: Optional[bool]


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class PortfolioPerformance(BaseModel):
    portfolio_id: int
    total_invested: float
    total_fees: float
    total_taxes: float
    net_cashflow: float
    current_value: float
    unrealized_pl: float
    realized_pl: float
    dividends_received: float


class CSVImportPreview(BaseModel):
    headers: List[str]
    rows: List[dict]
    checksum: float
    duplicates: int


class ImportResult(BaseModel):
    imported_transactions: int
    skipped_rows: int
    checksum_diff: float
