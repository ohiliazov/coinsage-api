from enum import Enum


class TransactionType(str, Enum):
    TRADE = "trade"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class ExchangeType(str, Enum):
    BINANCE = "binance"
