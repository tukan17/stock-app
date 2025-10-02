from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, get_db
from app.models.user import User
from app.services.brokers.fio import FIOBrokerParser

router = APIRouter()


@router.post("/fio/preview")
async def preview_fio_import(
    file: UploadFile,
    current_user: User = Depends(get_current_active_user)
):
    """
    Náhled importu z FIO brokera
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files are supported."
        )

    try:
        # Uložení souboru do dočasného umístění
        content = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(content)

        # Parsování CSV
        transactions = FIOBrokerParser.parse_csv("temp.csv")

        # Vrácení prvních 100 transakcí pro náhled
        return {
            "total_transactions": len(transactions),
            "preview": transactions[:100]
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error parsing file: {str(e)}"
        )
    finally:
        import os
        if os.path.exists("temp.csv"):
            os.remove("temp.csv")


@router.post("/fio/import")
async def import_fio_data(
    file: UploadFile,
    account_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import dat z FIO brokera
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files are supported."
        )

    try:
        # Uložení souboru do dočasného umístění
        content = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(content)

        # Parsování CSV
        transactions = FIOBrokerParser.parse_csv("temp.csv")

        # TODO: Import transakcí do DB
        # Pro každou transakci:
        # 1. Zkontrolovat existenci symbolu/aktiva
        # 2. Vytvořit nebo aktualizovat aktivum
        # 3. Vytvořit transakci
        # 4. Pro dividendy vytvořit dividend záznam
        # 5. Pro FX transakce zaznamenat převod měny

        return {
            "status": "success",
            "imported_transactions": len(transactions)
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error importing file: {str(e)}"
        )
    finally:
        import os
        if os.path.exists("temp.csv"):
            os.remove("temp.csv")