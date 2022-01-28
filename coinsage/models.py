from datetime import datetime
from decimal import Decimal
from typing import List

from sqlmodel import SQLModel, Field, Relationship
from .constants import TransactionType, ExchangeType


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    username: str
    password: str

    portfolios: List["Portfolio"] = Relationship(back_populates="user")


class Portfolio(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="user.id")
    name: str

    user: User = Relationship(back_populates="portfolios")
    transactions: List["Transaction"] = Relationship(
        back_populates="portfolio",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "single_parent": True,
        },
    )

    exchanges: List["Exchange"] = Relationship(back_populates="portfolio")


class Transaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    portfolio_id: int = Field(foreign_key="portfolio.id")

    transaction_type: TransactionType
    transaction_date: datetime

    buy_asset: str = None
    buy_amount: Decimal = 0

    sell_asset: str = None
    sell_amount: Decimal = 0

    fee_asset: str = None
    fee_amount: Decimal = 0

    external_id: str = None
    note: str = None

    portfolio: Portfolio = Relationship(back_populates="transactions")


class Exchange(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)

    portfolio_id: int = Field(foreign_key="portfolio.id")
    exchange_type: ExchangeType
    api_key: str
    secret_key: str

    portfolio: Portfolio = Relationship(back_populates="exchanges")
