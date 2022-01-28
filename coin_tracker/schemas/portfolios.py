from decimal import Decimal

from pydantic import BaseModel
from sqlmodel import SQLModel


class PortfolioCreate(SQLModel):
    name: str


class PortfolioRead(SQLModel):
    id: int
    user_id: int
    name: str


class PortfolioOverviewRead(BaseModel):
    asset: str
    amount: Decimal
