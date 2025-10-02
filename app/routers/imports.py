from __future__ import annotations

import csv
from io import StringIO
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/imports", tags=["imports"])


def _parse_csv(file: UploadFile) -> List[dict]:
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    return list(reader)


@router.post("/preview", response_model=schemas.CSVImportPreview)
def preview(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
    rows = _parse_csv(file)
    return crud.preview_import(rows)


@router.post("/ingest", response_model=schemas.ImportResult)
def ingest(
    portfolio_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
    rows = _parse_csv(file)
    accounts = crud.list_accounts(db, portfolio_id=portfolio_id)
    account_lookup = {account.account_name: account.id for account in accounts}
    return crud.ingest_transactions(db, rows, account_lookup)
