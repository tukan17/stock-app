from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/dividends", tags=["dividends"])


@router.post("/", response_model=schemas.Dividend, status_code=status.HTTP_201_CREATED)
def create_dividend(payload: schemas.DividendCreate, db: Session = Depends(get_db)):
    return crud.create_dividend(db, payload)


@router.get("/", response_model=list[schemas.Dividend])
def list_dividends(
    account_id: int | None = None,
    asset_id: int | None = None,
    upcoming_only: bool = False,
    db: Session = Depends(get_db),
):
    dividends = crud.list_dividends(db, account_id=account_id, asset_id=asset_id)
    if upcoming_only:
        today = date.today()
        dividends = [div for div in dividends if div.pay_date >= today]
    return dividends


@router.get("/{dividend_id}", response_model=schemas.Dividend)
def get_dividend(dividend_id: int, db: Session = Depends(get_db)):
    dividend = crud.get_dividend(db, dividend_id)
    if not dividend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return dividend


@router.put("/{dividend_id}", response_model=schemas.Dividend)
def update_dividend(dividend_id: int, payload: schemas.DividendUpdate, db: Session = Depends(get_db)):
    dividend = crud.get_dividend(db, dividend_id)
    if not dividend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    return crud.update_dividend(db, dividend, payload)


@router.delete("/{dividend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dividend(dividend_id: int, db: Session = Depends(get_db)):
    dividend = crud.get_dividend(db, dividend_id)
    if not dividend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dividend not found")
    crud.delete_dividend(db, dividend)
