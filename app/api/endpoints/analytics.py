from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from datetime import date, datetime, timedelta

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.models import Portfolio, Account, Transaction, Price, Asset
from app.services.portfolio_analytics import PortfolioAnalytics

router = APIRouter()


@router.get("/performance/")
def get_portfolio_performance(
    portfolio_id: uuid.UUID,
    start_date: date,
    end_date: date = None,
    period: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Získání výkonnosti portfolia za dané období
    """
    # Kontrola přístupu k portfoliu
    portfolio = db.query(Portfolio)\
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Nastavení koncového data
    if not end_date:
        end_date = date.today()
    
    # Přepsání období pokud je specifikováno
    if period:
        end_date = date.today()
        if period == "YTD":
            start_date = date(end_date.year, 1, 1)
        elif period == "1Y":
            start_date = end_date - timedelta(days=365)
        elif period == "3Y":
            start_date = end_date - timedelta(days=3*365)
        elif period == "5Y":
            start_date = end_date - timedelta(days=5*365)
    
    # Získání všech transakcí
    transactions = db.query(Transaction)\
        .join(Account)\
        .filter(
            Account.portfolio_id == portfolio_id,
            Transaction.trade_time.between(start_date, end_date)
        ).all()
    
    # Získání cen aktiv
    prices = db.query(Price)\
        .join(Asset)\
        .join(Transaction, Transaction.asset_id == Asset.id)\
        .join(Account)\
        .filter(
            Account.portfolio_id == portfolio_id,
            Price.date.between(start_date, end_date)
        ).all()
    
    # Výpočet TTWRR
    ttwrr = PortfolioAnalytics.calculate_ttwrr(
        [t.__dict__ for t in transactions],
        [p.__dict__ for p in prices],
        start_date,
        end_date
    )
    
    # Výpočet XIRR
    current_value = ttwrr['daily_values'][-1]['value'] if ttwrr['daily_values'] else 0
    xirr = PortfolioAnalytics.calculate_xirr(
        [t.__dict__ for t in transactions],
        current_value
    )
    
    # Výpočet rizikových metrik
    daily_returns = [
        (v['value'] - prev['value']) / prev['value']
        for v, prev in zip(ttwrr['daily_values'][1:], ttwrr['daily_values'][:-1])
    ]
    risk_metrics = PortfolioAnalytics.calculate_risk_metrics(daily_returns)
    
    # Benchmark comparison (pokud je nastaven)
    benchmark_comparison = None
    if portfolio.benchmark_id:
        benchmark_prices = db.query(Price)\
            .filter(
                Price.asset_id == portfolio.benchmark_id,
                Price.date.between(start_date, end_date)
            ).all()
        
        if benchmark_prices:
            benchmark_comparison = PortfolioAnalytics.calculate_benchmark_comparison(
                ttwrr['daily_values'],
                [{'date': p.date, 'value': p.close} for p in benchmark_prices]
            )
    
    return {
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'returns': {
            'ttwrr': ttwrr['annualized_return'],
            'xirr': xirr
        },
        'risk': risk_metrics,
        'benchmark': benchmark_comparison,
        'daily_values': ttwrr['daily_values']
    }


@router.get("/allocation/")
def get_portfolio_allocation(
    portfolio_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Získání alokace portfolia
    """
    # Kontrola přístupu k portfoliu
    portfolio = db.query(Portfolio)\
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Získání aktuálních držeb
    holdings = db.query(
        Asset.id,
        Asset.symbol,
        Asset.name,
        Asset.type,
        Asset.sector,
        Asset.region,
        Asset.currency,
        Transaction.quantity.label('quantity'),
        Price.close.label('price'),
        (Transaction.quantity * Price.close).label('market_value')
    ).join(Transaction)\
        .join(Account)\
        .join(Price)\
        .filter(
            Account.portfolio_id == portfolio_id,
            Transaction.quantity > 0
        ).all()
    
    # Výpočet vah
    total_value = sum(h.market_value for h in holdings)
    holdings_with_weight = [
        {**h.__dict__, 'weight': float(h.market_value / total_value)}
        for h in holdings
    ]
    
    # Výpočet alokace
    allocation = PortfolioAnalytics.calculate_asset_allocation(holdings_with_weight)
    
    return allocation