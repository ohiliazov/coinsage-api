from sqlmodel import SQLModel

from ..constants import ExchangeType


class ExchangeCreate(SQLModel):
    portfolio_id: int
    exchange_type: ExchangeType
    api_key: str
    secret_key: str


class ExchangeRead(SQLModel):
    id: int
    portfolio_id: int
    exchange_type: ExchangeType
