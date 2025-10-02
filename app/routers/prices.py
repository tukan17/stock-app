from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("/", response_model=schemas.Price, status_code=status.HTTP_201_CREATED)
def upsert_price(payload: schemas.PriceCreate, db: Session = Depends(get_db)):
    return crud.upsert_price(db, payload)


@router.get("/{asset_id}", response_model=list[schemas.Price])
def list_prices(asset_id: int, db: Session = Depends(get_db)):
    return crud.list_prices(db, asset_id)
