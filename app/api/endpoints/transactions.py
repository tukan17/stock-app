from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.models.models import Transaction, Account, Portfolio, Asset
from app.schemas.models import TransactionCreate, TransactionUpdate, Transaction as TransactionSchema

router = APIRouter()


def verify_account_access(
    db: Session,
    account_id: uuid.UUID,
    current_user: User
) -> Account:
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("/transactions/", response_model=List[TransactionSchema])
def read_transactions(
    account_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_account_access(db, account_id, current_user)
    
    query = db.query(Transaction).filter(Transaction.account_id == account_id)
    
    if start_date:
        query = query.filter(Transaction.trade_time >= start_date)
    if end_date:
        query = query.filter(Transaction.trade_time <= end_date)
    
    transactions = query.order_by(Transaction.trade_time.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return transactions


@router.post("/transactions/", response_model=TransactionSchema)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Ověření přístupu k účtu
    account = verify_account_access(db, transaction.account_id, current_user)
    
    # Ověření existence aktiva
    asset = db.query(Asset).filter(Asset.id == transaction.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Validace měn
    if transaction.trade_currency != account.currency and transaction.fx_rate_to_portfolio == 0:
        raise HTTPException(
            status_code=400,
            detail="FX rate must be provided for transactions in different currency"
        )
    
    # Validace hrubé částky
    calculated_gross = (
        transaction.quantity * transaction.price +
        transaction.fee +
        transaction.tax
    )
    if abs(calculated_gross - transaction.gross_amount) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Gross amount does not match calculation"
        )
    
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/transactions/{transaction_id}", response_model=TransactionSchema)
def read_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id
        ).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/transactions/{transaction_id}", response_model=TransactionSchema)
def update_transaction(
    transaction_id: uuid.UUID,
    transaction: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_transaction = db.query(Transaction)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id
        ).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Ověření přístupu k novému účtu, pokud se mění
    if transaction.account_id != db_transaction.account_id:
        verify_account_access(db, transaction.account_id, current_user)
    
    # Ověření existence aktiva
    if transaction.asset_id != db_transaction.asset_id:
        asset = db.query(Asset).filter(Asset.id == transaction.asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
    
    # Validace hrubé částky
    calculated_gross = (
        transaction.quantity * transaction.price +
        transaction.fee +
        transaction.tax
    )
    if abs(calculated_gross - transaction.gross_amount) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Gross amount does not match calculation"
        )
    
    for key, value in transaction.model_dump(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction)\
        .join(Account)\
        .join(Portfolio)\
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id
        ).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    return {"ok": True}