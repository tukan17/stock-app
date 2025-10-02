from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from decimal import Decimal


class AssetBase(BaseModel):
    symbol: str
    isin: Optional[str] = None
    name: str
    type: str
    sector: Optional[str] = None
    region: Optional[str] = None
    currency: str


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class Asset(AssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    account_id: uuid.UUID
    asset_id: uuid.UUID
    type: str
    quantity: Decimal
    price: Decimal
    fee: Decimal = Decimal(0)
    tax: Decimal = Decimal(0)
    gross_amount: Decimal
    trade_currency: str
    fx_rate_to_portfolio: Decimal
    trade_time: datetime
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DividendBase(BaseModel):
    account_id: uuid.UUID
    asset_id: uuid.UUID
    ex_date: datetime
    pay_date: datetime
    gross_amount: Decimal
    withholding_tax: Decimal
    net_amount: Decimal
    currency: str


class DividendCreate(DividendBase):
    pass


class DividendUpdate(DividendBase):
    pass


class Dividend(DividendBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PriceBase(BaseModel):
    asset_id: uuid.UUID
    date: datetime
    close: Decimal
    currency: str
    source: str


class PriceCreate(PriceBase):
    pass


class Price(PriceBase):
    class Config:
        from_attributes = True


class BenchmarkBase(BaseModel):
    symbol: str
    name: str
    currency: str


class BenchmarkCreate(BenchmarkBase):
    pass


class BenchmarkUpdate(BenchmarkBase):
    pass


class Benchmark(BenchmarkBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True