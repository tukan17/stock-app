from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, date

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.models import Dividend, Account, Portfolio, Asset
from app.schemas.models import DividendCreate, DividendUpdate, Dividend as DividendSchema

router = APIRouter()


@router.get("/dividends/", response_model=List[DividendSchema])
def read_dividends(
    account_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Ověření přístupu k účtu
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    query = db.query(Dividend).filter(Dividend.account_id == account_id)
    
    if start_date:
        query = query.filter(Dividend.pay_date >= start_date)
    if end_date:
        query = query.filter(Dividend.pay_date <= end_date)
    
    dividends = query.order_by(Dividend.pay_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return dividends


@router.post("/dividends/", response_model=DividendSchema)
def create_dividend(
    dividend: DividendCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Ověření přístupu k účtu
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == dividend.account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Ověření existence aktiva
    asset = db.query(Asset).filter(Asset.id == dividend.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Validace částek
    net_amount = dividend.gross_amount - dividend.withholding_tax
    if abs(net_amount - dividend.net_amount) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Net amount does not match gross amount minus withholding tax"
        )
    
    db_dividend = Dividend(**dividend.model_dump())
    db.add(db_dividend)
    db.commit()
    db.refresh(db_dividend)
    return db_dividend


@router.get("/dividends/{dividend_id}", response_model=DividendSchema)
def read_dividend(
    dividend_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    dividend = db.query(Dividend)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Dividend.id == dividend_id,
            Portfolio.user_id == current_user.id
        ).first()
    if dividend is None:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return dividend


@router.put("/dividends/{dividend_id}", response_model=DividendSchema)
def update_dividend(
    dividend_id: uuid.UUID,
    dividend: DividendUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_dividend = db.query(Dividend)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Dividend.id == dividend_id,
            Portfolio.user_id == current_user.id
        ).first()
    if db_dividend is None:
        raise HTTPException(status_code=404, detail="Dividend not found")
    
    # Validace částek
    net_amount = dividend.gross_amount - dividend.withholding_tax
    if abs(net_amount - dividend.net_amount) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Net amount does not match gross amount minus withholding tax"
        )
    
    for key, value in dividend.model_dump(exclude_unset=True).items():
        setattr(db_dividend, key, value)
    
    db.commit()
    db.refresh(db_dividend)
    return db_dividend


@router.delete("/dividends/{dividend_id}")
def delete_dividend(
    dividend_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    dividend = db.query(Dividend)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Dividend.id == dividend_id,
            Portfolio.user_id == current_user.id
        ).first()
    if dividend is None:
        raise HTTPException(status_code=404, detail="Dividend not found")
    
    db.delete(dividend)
    db.commit()
    return {"ok": True}


@router.get("/dividends/calendar/")
def dividend_calendar(
    account_id: uuid.UUID,
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Ověření přístupu k účtu
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    dividends = db.query(
        Dividend.asset_id,
        Asset.symbol,
        Asset.name,
        Dividend.ex_date,
        Dividend.pay_date,
        Dividend.gross_amount,
        Dividend.currency
    ).join(Asset)\
        .filter(
            Dividend.account_id == account_id,
            Dividend.pay_date.between(start_date, end_date)
        ).order_by(Dividend.pay_date)\
        .all()
    
    return [{
        "asset_id": str(d.asset_id),
        "symbol": d.symbol,
        "name": d.name,
        "ex_date": d.ex_date,
        "pay_date": d.pay_date,
        "gross_amount": float(d.gross_amount),
        "currency": d.currency
    } for d in dividends]