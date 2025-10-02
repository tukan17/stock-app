from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
import hashlib


class CSVColumnType(str, Enum):
    ACCOUNT = "account"
    DATE = "date"
    TYPE = "type"
    SYMBOL = "symbol"
    NAME = "name"
    QUANTITY = "quantity"
    PRICE = "price"
    FEE = "fee"
    TAX = "tax"
    CURRENCY = "currency"
    GROSS_AMOUNT = "gross_amount"
    NOTES = "notes"


class CSVMapping(BaseModel):
    name: str
    description: str
    column_mapping: Dict[CSVColumnType, str]
    date_format: str = "%Y-%m-%d %H:%M:%S"
    skip_rows: int = 0
    decimal_separator: str = "."
    thousands_separator: str = ","


class CSVImportPreview(BaseModel):
    total_rows: int
    preview_rows: List[Dict]
    checksum: str
    duplicates: List[Dict]


class CSVImportService:
    # Přednastavené mapování pro různé brokery
    PRESET_MAPPINGS = {
        "interactive_brokers": CSVMapping(
            name="Interactive Brokers",
            description="Import from Interactive Brokers activity report",
            column_mapping={
                CSVColumnType.ACCOUNT: "Account ID",
                CSVColumnType.DATE: "Date/Time",
                CSVColumnType.TYPE: "Type",
                CSVColumnType.SYMBOL: "Symbol",
                CSVColumnType.NAME: "Asset Name",
                CSVColumnType.QUANTITY: "Quantity",
                CSVColumnType.PRICE: "Price",
                CSVColumnType.FEE: "Commission",
                CSVColumnType.TAX: "Tax",
                CSVColumnType.CURRENCY: "Currency",
                CSVColumnType.GROSS_AMOUNT: "Amount",
                CSVColumnType.NOTES: "Notes"
            },
            date_format="%Y-%m-%d, %H:%M:%S",
            skip_rows=1
        ),
        "fio": CSVMapping(
            name="FIO broker",
            description="Import from FIO broker export (CSV)",
            column_mapping={
                CSVColumnType.DATE: "Datum obchodu",
                CSVColumnType.TYPE: "Směr",
                CSVColumnType.SYMBOL: "Symbol",
                CSVColumnType.PRICE: "Cena",
                CSVColumnType.QUANTITY: "Počet",
                CSVColumnType.CURRENCY: "Měna",
                CSVColumnType.GROSS_AMOUNT: "Objem v CZK",  # Prioritně používáme CZK
                CSVColumnType.FEE: "Poplatky v CZK",  # Prioritně používáme CZK
                CSVColumnType.NOTES: "Text FIO"
            },
            date_format="%d.%m.%Y %H:%M",
            decimal_separator=",",
            thousands_separator=" "
        ),
        "revolut": CSVMapping(
            name="Revolut",
            description="Import from Revolut trading history",
            column_mapping={
                CSVColumnType.DATE: "Date",
                CSVColumnType.TYPE: "Type",
                CSVColumnType.SYMBOL: "Ticker",
                CSVColumnType.NAME: "Name",
                CSVColumnType.QUANTITY: "Shares",
                CSVColumnType.PRICE: "Price per share",
                CSVColumnType.GROSS_AMOUNT: "Total Amount",
                CSVColumnType.CURRENCY: "Currency"
            },
            date_format="%Y-%m-%d %H:%M:%S"
        ),
        # Další přednastavená mapování pro jiné brokery...
    }

    @staticmethod
    def _calculate_row_hash(row: Dict) -> str:
        """Vytvoří hash z klíčových hodnot řádku pro detekci duplicit"""
        key_values = [
            str(row.get(col.value, "")) for col in [
                CSVColumnType.ACCOUNT,
                CSVColumnType.DATE,
                CSVColumnType.TYPE,
                CSVColumnType.SYMBOL,
                CSVColumnType.QUANTITY,
                CSVColumnType.PRICE
            ]
        ]
        return hashlib.sha256("|".join(key_values).encode()).hexdigest()

    @staticmethod
    def preview_import(
        file_path: str,
        mapping: CSVMapping,
        preview_rows: int = 100
    ) -> CSVImportPreview:
        """
        Načte CSV soubor a vrátí náhled dat včetně kontrolního součtu
        """
        # Načtení CSV s použitím mapování
        df = pd.read_csv(
            file_path,
            skiprows=mapping.skip_rows,
            decimal=mapping.decimal_separator,
            thousands=mapping.thousands_separator
        )

        # Přejmenování sloupců podle mapování
        reverse_mapping = {v: k.value for k, v in mapping.column_mapping.items()}
        df = df.rename(columns=reverse_mapping)

        # Převod data
        if CSVColumnType.DATE.value in df.columns:
            df[CSVColumnType.DATE.value] = pd.to_datetime(
                df[CSVColumnType.DATE.value],
                format=mapping.date_format
            )

        # Výpočet kontrolního součtu
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df).values.tobytes()
        ).hexdigest()

        # Detekce duplicit
        df['row_hash'] = df.apply(
            lambda row: CSVImportService._calculate_row_hash(row.to_dict()),
            axis=1
        )
        duplicates = df[df.duplicated('row_hash', keep=False)]\
            .sort_values('row_hash')\
            .head(preview_rows)\
            .to_dict('records')

        # Příprava náhledu
        preview = df.head(preview_rows).to_dict('records')

        return CSVImportPreview(
            total_rows=len(df),
            preview_rows=preview,
            checksum=checksum,
            duplicates=duplicates
        )

    @staticmethod
    def import_csv(
        file_path: str,
        mapping: CSVMapping,
        checksum: str
    ) -> List[Dict]:
        """
        Importuje data z CSV souboru podle mapování
        """
        # Načtení CSV
        df = pd.read_csv(
            file_path,
            skiprows=mapping.skip_rows,
            decimal=mapping.decimal_separator,
            thousands=mapping.thousands_separator
        )

        # Ověření kontrolního součtu
        current_checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df).values.tobytes()
        ).hexdigest()
        
        if current_checksum != checksum:
            raise ValueError("Checksum mismatch - file has changed since preview")

        # Přejmenování sloupců
        reverse_mapping = {v: k.value for k, v in mapping.column_mapping.items()}
        df = df.rename(columns=reverse_mapping)

        # Převod data
        if CSVColumnType.DATE.value in df.columns:
            df[CSVColumnType.DATE.value] = pd.to_datetime(
                df[CSVColumnType.DATE.value],
                format=mapping.date_format
            )

        # Vrácení všech řádků jako seznam slovníků
        return df.to_dict('records')