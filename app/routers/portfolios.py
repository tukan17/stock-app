from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("/", response_model=schemas.Portfolio, status_code=status.HTTP_201_CREATED)
def create_portfolio(payload: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    return crud.create_portfolio(db, payload)


@router.get("/", response_model=list[schemas.Portfolio])
def list_portfolios(user_id: int | None = None, db: Session = Depends(get_db)):
    return crud.list_portfolios(db, user_id=user_id)


@router.get("/{portfolio_id}", response_model=schemas.Portfolio)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.put("/{portfolio_id}", response_model=schemas.Portfolio)
def update_portfolio(portfolio_id: int, payload: schemas.PortfolioUpdate, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud.update_portfolio(db, portfolio, payload)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    crud.delete_portfolio(db, portfolio)


@router.get("/{portfolio_id}/performance", response_model=schemas.PortfolioPerformance)
def portfolio_performance(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud.compute_portfolio_performance(db, portfolio_id)
