from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from . import models, schemas


# User CRUD


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(**payload.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(db: Session, user: models.User, payload: schemas.UserUpdate) -> models.User:
    return update_entity(db, user, payload)


def delete_user(db: Session, user: models.User) -> None:
    db.delete(user)
    db.commit()


def create_entity(db: Session, model, schema):
    instance = model(**schema.dict())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def update_entity(db: Session, instance, schema):
    data = schema.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(instance, field, value)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


# Portfolio CRUD

def create_portfolio(db: Session, payload: schemas.PortfolioCreate) -> models.Portfolio:
    portfolio = models.Portfolio(**payload.dict())
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def list_portfolios(db: Session, user_id: Optional[int] = None) -> List[models.Portfolio]:
    query = db.query(models.Portfolio)
    if user_id is not None:
        query = query.filter(models.Portfolio.user_id == user_id)
    return query.all()


def get_portfolio(db: Session, portfolio_id: int) -> Optional[models.Portfolio]:
    return db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()


def update_portfolio(
    db: Session, portfolio: models.Portfolio, payload: schemas.PortfolioUpdate
) -> models.Portfolio:
    return update_entity(db, portfolio, payload)


def delete_portfolio(db: Session, portfolio: models.Portfolio) -> None:
    db.delete(portfolio)
    db.commit()


# Account CRUD

def create_account(db: Session, payload: schemas.AccountCreate) -> models.Account:
    account = models.Account(**payload.dict())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def list_accounts(db: Session, portfolio_id: Optional[int] = None) -> List[models.Account]:
    query = db.query(models.Account)
    if portfolio_id is not None:
        query = query.filter(models.Account.portfolio_id == portfolio_id)
    return query.all()


def get_account(db: Session, account_id: int) -> Optional[models.Account]:
    return db.query(models.Account).filter(models.Account.id == account_id).first()


def update_account(db: Session, account: models.Account, payload: schemas.AccountUpdate) -> models.Account:
    return update_entity(db, account, payload)


def delete_account(db: Session, account: models.Account) -> None:
    db.delete(account)
    db.commit()


# Asset CRUD

def create_asset(db: Session, payload: schemas.AssetCreate) -> models.Asset:
    asset = models.Asset(**payload.dict())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session) -> List[models.Asset]:
    return db.query(models.Asset).all()


def get_asset(db: Session, asset_id: int) -> Optional[models.Asset]:
    return db.query(models.Asset).filter(models.Asset.id == asset_id).first()


def update_asset(db: Session, asset: models.Asset, payload: schemas.AssetUpdate) -> models.Asset:
    return update_entity(db, asset, payload)


def delete_asset(db: Session, asset: models.Asset) -> None:
    db.delete(asset)
    db.commit()


# Transaction CRUD

def create_transaction(
    db: Session, payload: schemas.TransactionCreate
) -> models.Transaction:
    transaction = models.Transaction(**payload.dict())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(
    db: Session, account_id: Optional[int] = None, portfolio_id: Optional[int] = None
) -> List[models.Transaction]:
    query = db.query(models.Transaction)
    if account_id is not None:
        query = query.filter(models.Transaction.account_id == account_id)
    if portfolio_id is not None:
        query = query.join(models.Account).filter(models.Account.portfolio_id == portfolio_id)
    return query.order_by(models.Transaction.trade_time.desc()).all()


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id)
        .first()
    )


def update_transaction(
    db: Session, transaction: models.Transaction, payload: schemas.TransactionUpdate
) -> models.Transaction:
    return update_entity(db, transaction, payload)


def delete_transaction(db: Session, transaction: models.Transaction) -> None:
    db.delete(transaction)
    db.commit()


# Dividend CRUD

def create_dividend(db: Session, payload: schemas.DividendCreate) -> models.Dividend:
    dividend = models.Dividend(**payload.dict())
    db.add(dividend)
    db.commit()
    db.refresh(dividend)
    return dividend


def list_dividends(
    db: Session, account_id: Optional[int] = None, asset_id: Optional[int] = None
) -> List[models.Dividend]:
    query = db.query(models.Dividend)
    if account_id is not None:
        query = query.filter(models.Dividend.account_id == account_id)
    if asset_id is not None:
        query = query.filter(models.Dividend.asset_id == asset_id)
    return query.order_by(models.Dividend.pay_date.desc()).all()


def get_dividend(db: Session, dividend_id: int) -> Optional[models.Dividend]:
    return db.query(models.Dividend).filter(models.Dividend.id == dividend_id).first()


def update_dividend(
    db: Session, dividend: models.Dividend, payload: schemas.DividendUpdate
) -> models.Dividend:
    return update_entity(db, dividend, payload)


def delete_dividend(db: Session, dividend: models.Dividend) -> None:
    db.delete(dividend)
    db.commit()


# Price CRUD

def upsert_price(db: Session, payload: schemas.PriceCreate) -> models.Price:
    price = (
        db.query(models.Price)
        .filter(models.Price.asset_id == payload.asset_id, models.Price.date == payload.date)
        .first()
    )
    if price:
        for field, value in payload.dict().items():
            setattr(price, field, value)
    else:
        price = models.Price(**payload.dict())
        db.add(price)
    db.commit()
    db.refresh(price)
    return price


def list_prices(db: Session, asset_id: int) -> List[models.Price]:
    return (
        db.query(models.Price)
        .filter(models.Price.asset_id == asset_id)
        .order_by(models.Price.date.desc())
        .all()
    )


# Benchmark CRUD

def create_benchmark(db: Session, payload: schemas.BenchmarkCreate) -> models.Benchmark:
    benchmark = models.Benchmark(**payload.dict())
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    return benchmark


def list_benchmarks(db: Session) -> List[models.Benchmark]:
    return db.query(models.Benchmark).all()


def get_benchmark(db: Session, benchmark_id: int) -> Optional[models.Benchmark]:
    return (
        db.query(models.Benchmark)
        .filter(models.Benchmark.id == benchmark_id)
        .first()
    )


def update_benchmark(
    db: Session, benchmark: models.Benchmark, payload: schemas.BenchmarkUpdate
) -> models.Benchmark:
    return update_entity(db, benchmark, payload)


def delete_benchmark(db: Session, benchmark: models.Benchmark) -> None:
    db.delete(benchmark)
    db.commit()


def compute_portfolio_performance(db: Session, portfolio_id: int) -> schemas.PortfolioPerformance:
    transactions = list_transactions(db, portfolio_id=portfolio_id)
    accounts = list_accounts(db, portfolio_id=portfolio_id)
    account_ids = {account.id for account in accounts}
    dividends = (
        db.query(models.Dividend)
        .filter(models.Dividend.account_id.in_(account_ids))
        .all()
        if account_ids
        else []
    )

    invested = Decimal("0")
    fees = Decimal("0")
    taxes = Decimal("0")
    realized_pl = Decimal("0")
    position_qty: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    position_cost: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))

    for txn in transactions:
        qty = Decimal(txn.qty)
        price = Decimal(txn.price)
        gross = Decimal(txn.gross_amount) if txn.gross_amount is not None else qty * price
        sign = Decimal("1") if txn.type in {"BUY", "FEE", "TAX"} else Decimal("-1")
        invested += gross * sign
        fees += Decimal(txn.fee or 0)
        taxes += Decimal(txn.tax or 0)

        if txn.type == "BUY":
            position_qty[txn.asset_id] += qty
            position_cost[txn.asset_id] += gross + Decimal(txn.fee or 0) + Decimal(txn.tax or 0)
        elif txn.type == "SELL":
            held_qty = position_qty[txn.asset_id]
            average_cost = (
                position_cost[txn.asset_id] / held_qty if held_qty else Decimal("0")
            )
            position_qty[txn.asset_id] = held_qty - qty
            realized_pl += gross - qty * average_cost
            position_cost[txn.asset_id] -= qty * average_cost

    latest_prices: dict[int, Decimal] = {}
    price_query = (
        db.query(models.Price)
        .filter(models.Price.asset_id.in_(position_qty.keys()))
        .order_by(models.Price.asset_id, models.Price.date.desc())
    )
    for price in price_query:
        if price.asset_id not in latest_prices:
            latest_prices[price.asset_id] = Decimal(price.close)

    current_value = Decimal("0")
    for asset_id, qty in position_qty.items():
        price = latest_prices.get(asset_id)
        if price is None:
            continue
        current_value += qty * price

    dividends_received = sum(Decimal(div.net) for div in dividends if div.account.portfolio_id == portfolio_id)

    net_cashflow = invested + dividends_received
    unrealized_pl = current_value + dividends_received - invested

    return schemas.PortfolioPerformance(
        portfolio_id=portfolio_id,
        total_invested=float(invested),
        total_fees=float(fees),
        total_taxes=float(taxes),
        net_cashflow=float(net_cashflow),
        current_value=float(current_value),
        unrealized_pl=float(unrealized_pl),
        realized_pl=float(realized_pl),
        dividends_received=float(dividends_received),
    )


def preview_import(rows: Sequence[dict]) -> schemas.CSVImportPreview:
    headers = list(rows[0].keys()) if rows else []
    checksum = sum(float(row.get("GrossAmount", 0) or 0) for row in rows)
    dedup_keys = set()
    duplicates = 0
    for row in rows:
        key = (
            row.get("Account"),
            row.get("Date"),
            row.get("Ticker/ISIN"),
            row.get("Qty"),
            row.get("Price"),
        )
        if key in dedup_keys:
            duplicates += 1
        else:
            dedup_keys.add(key)
    return schemas.CSVImportPreview(headers=headers, rows=list(rows[:100]), checksum=checksum, duplicates=duplicates)


def ingest_transactions(db: Session, rows: Sequence[dict], account_lookup: dict[str, int]) -> schemas.ImportResult:
    imported = 0
    skipped = 0
    checksum = Decimal("0")

    for row in rows:
        account_name = row.get("Account")
        account_id = account_lookup.get(account_name)
        if not account_id:
            skipped += 1
            continue
        asset_symbol = row.get("Ticker/ISIN") or row.get("Ticker")
        asset = (
            db.query(models.Asset).filter(models.Asset.symbol == asset_symbol).first()
        )
        if not asset:
            asset = models.Asset(
                symbol=asset_symbol,
                name=row.get("Name") or asset_symbol,
                type="stock",
                currency=row.get("Currency") or "USD",
            )
            db.add(asset)
            db.flush()
        transaction = models.Transaction(
            account_id=account_id,
            asset_id=asset.id,
            type=row.get("Type", "BUY"),
            qty=Decimal(row.get("Qty") or 0),
            price=Decimal(row.get("Price") or 0),
            fee=Decimal(row.get("Fee") or 0),
            tax=Decimal(row.get("Tax") or 0),
            gross_amount=Decimal(row.get("GrossAmount") or 0),
            trade_currency=row.get("Currency") or "USD",
            trade_time=datetime.fromisoformat(row.get("Date")),
        )
        db.add(transaction)
        checksum += Decimal(row.get("Qty") or 0) * Decimal(row.get("Price") or 0)
        imported += 1
    db.commit()

    checksum_diff = float(checksum - sum(Decimal(row.get("GrossAmount") or 0) for row in rows))

    return schemas.ImportResult(
        imported_transactions=imported,
        skipped_rows=skipped,
        checksum_diff=checksum_diff,
    )
