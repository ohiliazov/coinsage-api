from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel

from ..constants import TransactionType


class TransactionCreate(SQLModel):
    portfolio_id: int
    transaction_type: TransactionType
    transaction_date: datetime

    buy_asset: str = None
    buy_amount: Decimal = Decimal()
    sell_asset: str = None
    sell_amount: Decimal = Decimal()
    fee_asset: str = None
    fee_amount: Decimal = Decimal()

    note: str = None


class TransactionRead(SQLModel):
    id: int
    portfolio_id: int
    transaction_type: TransactionType
    transaction_date: datetime

    buy_asset: str = None
    buy_amount: Decimal
    sell_asset: str = None
    sell_amount: Decimal
    fee_asset: str = None
    fee_amount: Decimal

    note: str = None
