from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
import json
from typing import List
import uuid
import tempfile
import os

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.services.csv_import import CSVImportService, CSVMapping, CSVImportPreview
from app.models.models import Portfolio, Account, Transaction

router = APIRouter()


@router.get("/import/presets")
def get_import_presets():
    """Získání předdefinovaných mapování pro různé brokery"""
    return CSVImportService.PRESET_MAPPINGS


@router.post("/import/preview", response_model=CSVImportPreview)
async def preview_import(
    file: UploadFile = File(...),
    mapping_json: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Náhled importu CSV souboru
    """
    try:
        mapping = CSVMapping.model_validate_json(mapping_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid mapping: {str(e)}")

    # Uložení souboru do dočasného adresáře
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()

        try:
            preview = CSVImportService.preview_import(
                temp_file.name,
                mapping,
                preview_rows=100
            )
        finally:
            os.unlink(temp_file.name)

    return preview


@router.post("/import/execute")
async def execute_import(
    file: UploadFile = File(...),
    mapping_json: str = Form(...),
    checksum: str = Form(...),
    account_id: uuid.UUID = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Provedení importu CSV souboru
    """
    # Ověření přístupu k účtu
    account = db.query(Account)\
        .join(Portfolio)\
        .filter(
            Account.id == account_id,
            Portfolio.user_id == current_user.id
        ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        mapping = CSVMapping.model_validate_json(mapping_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid mapping: {str(e)}")

    # Uložení souboru do dočasného adresáře
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()

        try:
            # Import dat
            imported_data = CSVImportService.import_csv(
                temp_file.name,
                mapping,
                checksum
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            os.unlink(temp_file.name)

    # Vytvoření transakcí v DB
    transactions = []
    for row in imported_data:
        transaction = Transaction(
            account_id=account_id,
            trade_time=row['date'],
            type=row['type'],
            symbol=row['symbol'],
            quantity=row['quantity'],
            price=row['price'],
            fee=row.get('fee', 0),
            tax=row.get('tax', 0),
            gross_amount=row['gross_amount'],
            currency=row['currency'],
            notes=row.get('notes')
        )
        transactions.append(transaction)

    db.add_all(transactions)
    db.commit()

    return {
        "status": "success",
        "imported_rows": len(transactions)
    }