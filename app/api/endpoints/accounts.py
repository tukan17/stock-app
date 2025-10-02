from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.models import Account, Portfolio
from app.schemas.user import AccountCreate, AccountUpdate, Account as AccountSchema

router = APIRouter()


def verify_portfolio_access(
    db: Session,
    portfolio_id: uuid.UUID,
    current_user: User
) -> Portfolio:
    portfolio = db.query(Portfolio)\
        .filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)\
        .first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.get("/accounts/", response_model=List[AccountSchema])
def read_accounts(
    portfolio_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_portfolio_access(db, portfolio_id, current_user)
    accounts = db.query(Account)\
        .filter(Account.portfolio_id == portfolio_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return accounts


@router.post("/accounts/", response_model=AccountSchema)
def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_portfolio_access(db, account.portfolio_id, current_user)
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/accounts/{account_id}", response_model=AccountSchema)
def read_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=AccountSchema)
def update_account(
    account_id: uuid.UUID,
    account: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in account.model_dump(exclude_unset=True).items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(account)
    db.commit()
    return {"ok": True}