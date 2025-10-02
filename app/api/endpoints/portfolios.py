from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.auth import get_current_active_user, get_db
from app.models.models import Portfolio
from app.models.user import User
from app.schemas.user import PortfolioCreate, PortfolioUpdate, Portfolio as PortfolioSchema

router = APIRouter()


@router.get("/portfolios/", response_model=List[PortfolioSchema])
def read_portfolios(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    portfolios = db.query(Portfolio)\
        .filter(Portfolio.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return portfolios


@router.post("/portfolios/", response_model=PortfolioSchema)
def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_portfolio = Portfolio(**portfolio.model_dump(), user_id=current_user.id)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioSchema)
def read_portfolio(
    portfolio_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio)\
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)\
        .first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioSchema)
def update_portfolio(
    portfolio_id: uuid.UUID,
    portfolio: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_portfolio = db.query(Portfolio)\
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)\
        .first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    for key, value in portfolio.model_dump(exclude_unset=True).items():
        setattr(db_portfolio, key, value)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


@router.delete("/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio)\
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)\
        .first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(portfolio)
    db.commit()
    return {"ok": True}