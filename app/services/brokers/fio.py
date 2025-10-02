from datetime import datetime
from typing import Dict, List
import pandas as pd
from decimal import Decimal


class FIOBrokerParser:
    """Parser pro import dat z FIO brokera"""

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Převede string na datum"""
        if not date_str:
            return None
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M")

    @staticmethod
    def parse_number(number_str: str) -> Decimal:
        """Převede string na číslo"""
        if not number_str or number_str == "0,00":
            return Decimal("0")
        return Decimal(number_str.replace(",", ".").replace(" ", ""))

    @staticmethod
    def parse_direction(direction: str) -> str:
        """Převede směr obchodu na standardní typ"""
        if not direction:
            return None
        direction_map = {
            "Nákup": "BUY",
            "Prodej": "SELL",
            "Převod mezi měnami": "FX"
        }
        return direction_map.get(direction)

    @staticmethod
    def get_transaction_type(row: Dict) -> str:
        """Určí typ transakce z dat"""
        if "Dividenda" in str(row["Text FIO"]):
            return "DIVIDEND"
        elif "Daň z divid." in str(row["Text FIO"]):
            return "TAX"
        elif "ADR Fee" in str(row["Text FIO"]):
            return "FEE"
        elif row["Směr"] == "Nákup":
            return "BUY"
        elif row["Směr"] == "Prodej":
            return "SELL"
        elif row["Směr"] == "Převod mezi měnami":
            return "FX"
        elif "Poplatek" in str(row["Text FIO"]):
            return "FEE"
        elif "Vloženo na účet" in str(row["Text FIO"]):
            return "DEPOSIT"
        return None

    @staticmethod
    def get_transaction_currency(row: Dict) -> str:
        """Určí měnu transakce"""
        if row["Objem v USD"] and row["Objem v USD"] != "0,00":
            return "USD"
        elif row["Objem v EUR"] and row["Objem v EUR"] != "0,00":
            return "EUR"
        elif row["Objem v CZK"] and row["Objem v CZK"] != "0,00":
            return "CZK"
        return row["Měna"]

    @staticmethod
    def get_transaction_amount(row: Dict, currency: str) -> Decimal:
        """Získá objem transakce v dané měně"""
        amount_map = {
            "USD": "Objem v USD",
            "EUR": "Objem v EUR",
            "CZK": "Objem v CZK"
        }
        amount = row[amount_map.get(currency, "")]
        return FIOBrokerParser.parse_number(amount) if amount else Decimal("0")

    @staticmethod
    def get_transaction_fee(row: Dict, currency: str) -> Decimal:
        """Získá poplatek v dané měně"""
        fee_map = {
            "USD": "Poplatky v USD",
            "EUR": "Poplatky v EUR",
            "CZK": "Poplatky v CZK"
        }
        fee = row[fee_map.get(currency, "")]
        return FIOBrokerParser.parse_number(fee) if fee else Decimal("0")

    @classmethod
    def parse_csv(cls, file_path: str) -> List[Dict]:
        """
        Zpracuje CSV soubor z FIO a vrátí seznam transakcí
        """
        # Načtení CSV
        df = pd.read_csv(
            file_path,
            encoding="windows-1250",  # FIO používá windows-1250 kódování
            decimal=",",
            thousands=" "
        )

        # Vyčištění prázdných řádků
        df = df.dropna(how="all")

        transactions = []
        
        for _, row in df.iterrows():
            # Základní informace o transakci
            trans_type = cls.get_transaction_type(row)
            if not trans_type:
                continue

            currency = cls.get_transaction_currency(row)
            if not currency:
                continue

            date = cls.parse_date(row["Datum obchodu"])
            if not date:
                continue

            # Vytvoření transakce
            transaction = {
                "date": date,
                "type": trans_type,
                "symbol": row["Symbol"] if pd.notna(row["Symbol"]) else None,
                "currency": currency
            }

            # Zpracování podle typu transakce
            if trans_type in ["BUY", "SELL"]:
                transaction.update({
                    "quantity": cls.parse_number(row["Počet"]),
                    "price": cls.parse_number(row["Cena"]),
                    "amount": abs(cls.get_transaction_amount(row, currency)),
                    "fee": cls.get_transaction_fee(row, currency)
                })
            elif trans_type == "DIVIDEND":
                transaction.update({
                    "amount": cls.get_transaction_amount(row, currency),
                    "quantity": 1,  # Dividend je vždy jedna
                    "price": cls.get_transaction_amount(row, currency),
                    "fee": Decimal("0")
                })
            elif trans_type == "TAX":
                transaction.update({
                    "amount": abs(cls.get_transaction_amount(row, currency)),
                    "quantity": 1,
                    "price": abs(cls.get_transaction_amount(row, currency)),
                    "fee": Decimal("0")
                })
            elif trans_type == "FEE":
                transaction.update({
                    "amount": abs(cls.get_transaction_amount(row, currency)),
                    "quantity": 1,
                    "price": abs(cls.get_transaction_amount(row, currency)),
                    "fee": cls.get_transaction_fee(row, currency)
                })
            elif trans_type == "FX":
                # Pro FX transakce potřebujeme obě měny a kurz
                source_amount = cls.get_transaction_amount(row, row["Měna"])
                target_currency = "USD" if row["Objem v USD"] else ("EUR" if row["Objem v EUR"] else "CZK")
                target_amount = cls.get_transaction_amount(row, target_currency)
                
                transaction.update({
                    "source_currency": row["Měna"],
                    "target_currency": target_currency,
                    "source_amount": abs(source_amount),
                    "target_amount": abs(target_amount),
                    "fx_rate": abs(target_amount / source_amount) if source_amount else None,
                    "fee": cls.get_transaction_fee(row, target_currency)
                })
            elif trans_type == "DEPOSIT":
                transaction.update({
                    "amount": cls.get_transaction_amount(row, currency),
                    "quantity": 1,
                    "price": cls.get_transaction_amount(row, currency),
                    "fee": Decimal("0")
                })

            # Přidání poznámky
            if pd.notna(row["Text FIO"]):
                transaction["notes"] = row["Text FIO"]

            transactions.append(transaction)

        return transactions