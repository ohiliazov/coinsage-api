from datetime import datetime, timedelta

from dateutil.rrule import rrule, DAILY
from sqlmodel import Session, select

from coinsage.models import Transaction
from coinsage.exchanges.binance_api import BinanceAPI


class TransactionMapper:
    def __init__(self, portfolio_id: int):
        self.portfolio_id = portfolio_id

    def from_deposit_history(self, data: dict) -> Transaction:
        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="deposit",
            transaction_date=data["insertTime"] / 1000,
            buy_asset=data["coin"],
            buy_amount=data["amount"],
            external_id=f"deposit_history__{data['id']}",
        )

    def from_withdraw_history(self, data: dict) -> Transaction:
        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="withdraw",
            transaction_date=datetime.fromisoformat(data["applyTime"]),
            sell_asset=data["coin"],
            sell_amount=data["amount"],
            fee_asset=data["coin"],
            fee_amount=data["transactionFee"],
            external_id=f"withdraw_history__{data['id']}",
        )

    def from_asset_dividend(self, data: dict) -> Transaction:
        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="trade",
            transaction_date=data["divTime"] / 1000,
            buy_asset=data["asset"],
            buy_amount=data["amount"],
            external_id=f"asset_dividend__{data['id']}",
        )

    def from_asset_dribblet(self, data: dict) -> Transaction:
        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="trade",
            transaction_date=data["operateTime"] / 1000,
            buy_asset="BNB",
            buy_amount=data["transferedAmount"],
            sell_asset=data["fromAsset"],
            sell_amount=data["amount"],
            fee_asset="BNB",
            fee_amount=data["serviceChargeAmount"],
            external_id=f"asset_dribblet__{data['transId']}",
        )

    def from_fiat_orders(self, data: dict, tran_type: int):
        if tran_type == 0:  # deposit
            transaction_type = "deposit"
            buy_asset = data["fiatCurrency"]
            buy_amount = data["amount"]
            sell_asset = None
            sell_amount = 0
        else:  # withdraw
            transaction_type = "withdraw"
            buy_asset = None
            buy_amount = 0
            sell_asset = data["fiatCurrency"]
            sell_amount = data["amount"]

        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type=transaction_type,
            transaction_date=data["updateTime"] / 1000,
            buy_asset=buy_asset,
            buy_amount=buy_amount,
            sell_asset=sell_asset,
            sell_amount=sell_amount,
            fee_asset=data["fiatCurrency"],
            fee_amount=data["totalFee"],
            external_id=f"fiat_orders__{data['orderNo']}",
        )

    def from_fiat_payments(self, data: dict, tran_type: int):
        if tran_type == 0:  # buy
            buy_asset = data["cryptoCurrency"]
            sell_asset = data["fiatCurrency"]
        else:  # sell
            buy_asset = data["fiatCurrency"]
            sell_asset = data["cryptoCurrency"]

        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="trade",
            transaction_date=data["updateTime"] / 1000,
            buy_asset=buy_asset,
            buy_amount=data["obtainAmount"],
            sell_asset=sell_asset,
            sell_amount=data["sourceAmount"],
            fee_asset=data["fiatCurrency"],
            fee_amount=data["totalFee"],
            external_id=f"fiat_payments__{data['orderNo']}",
        )

    def from_trade_flow(self, data: dict) -> Transaction:
        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="trade",
            transaction_date=data["createTime"] / 1000,
            buy_asset=data["toAsset"],
            buy_amount=data["toAmount"],
            sell_asset=data["fromAsset"],
            sell_amount=data["fromAmount"],
            external_id=f"trade_flow__{data['orderId']}",
        )

    def from_my_trades(self, symbol: dict, data: dict) -> Transaction:
        if data["isBuyer"]:
            buy_currency = symbol["baseAsset"]
            buy_amount = data["qty"]
            sell_currency = symbol["quoteAsset"]
            sell_amount = data["quoteQty"]
        else:
            buy_currency = symbol["quoteAsset"]
            buy_amount = data["quoteQty"]
            sell_currency = symbol["baseAsset"]
            sell_amount = data["qty"]

        return Transaction(
            portfolio_id=self.portfolio_id,
            transaction_type="trade",
            transaction_date=data["time"] / 1000,
            buy_asset=buy_currency,
            buy_amount=buy_amount,
            sell_asset=sell_currency,
            sell_amount=sell_amount,
            fee_asset=data["commissionAsset"],
            fee_amount=data["commission"],
            external_id=f"my_trades__{data['id']}",
        )


class BinanceImporter:
    def __init__(
        self,
        session: Session,
        portfolio_id: int,
        api_key,
        secret_key,
        start_date: datetime.date,
        end_date: datetime.date = datetime.utcnow(),
    ):
        self.session = session
        self.portfolio_id = portfolio_id
        self.api = BinanceAPI(api_key, secret_key)
        self.start_date = start_date
        self.end_date = end_date

        self.existing_ids = self.session.exec(
            select(Transaction.external_id).where(
                Transaction.portfolio_id == portfolio_id,
                Transaction.external_id.is_not(None),
            )
        ).all()
        self.mapper = TransactionMapper(portfolio_id)

    def add_transaction(self, transaction: Transaction):
        if transaction.external_id not in self.existing_ids:
            print(f"NEW TRANSACTION: {transaction.external_id}")
            self.session.add(transaction)

    def import_deposit_history(self):
        print("DEPOSIT HISTORY: START")

        deposit_history = self.api.deposit_history()

        for item in deposit_history:
            transaction = self.mapper.from_deposit_history(item)
            self.add_transaction(transaction)

        print("DEPOSIT HISTORY: DONE")

    def import_withdraw_history(self):
        print("WITHDRAW HISTORY: START")

        withdraw_history = self.api.withdraw_history()

        for item in withdraw_history:
            transaction = self.mapper.from_withdraw_history(item)
            self.add_transaction(transaction)
        self.session.commit()

        print("WITHDRAW HISTORY: DONE")

    def import_asset_dividends(self):
        print("ASSET DIVIDENDS: START")
        asset_dividends = self.api.asset_dividends()

        for item in asset_dividends:
            transaction = self.mapper.from_asset_dividend(item)
            self.add_transaction(transaction)
        self.session.commit()

        print("ASSET DIVIDENDS: DONE")

    def import_asset_dribblets(self):
        print("ASSET DRIBBLETS: START")
        asset_dribblets = self.api.asset_dribblets()

        for item in asset_dribblets:
            transaction = self.mapper.from_asset_dribblet(item)
            self.add_transaction(transaction)
        self.session.commit()

        print("ASSET DRIBBLETS: DONE")

    def import_fiat_orders(self):
        print("FIAT ORDERS: START")

        fiat_orders_buy = self.api.fiat_orders(
            0,
            begin_time=self.start_date,
            end_time=self.end_date,
        )
        fiat_orders_sell = self.api.fiat_orders(
            1,
            begin_time=self.start_date,
            end_time=self.end_date,
        )

        for item in fiat_orders_buy:
            transaction = self.mapper.from_fiat_orders(item, 0)
            self.add_transaction(transaction)

        for item in fiat_orders_sell:
            transaction = self.mapper.from_fiat_orders(item, 1)
            self.add_transaction(transaction)
        self.session.commit()

        print("FIAT ORDERS: DONE")

    def import_fiat_payments(self):
        print("FIAT PAYMENTS: START")

        fiat_payments_buy = self.api.fiat_payments(
            0,
            begin_time=self.start_date,
            end_time=self.end_date,
        )
        fiat_payments_sell = self.api.fiat_payments(
            1,
            begin_time=self.start_date,
            end_time=self.end_date,
        )

        for item in fiat_payments_buy:
            transaction = self.mapper.from_fiat_payments(item, 0)
            self.add_transaction(transaction)

        for item in fiat_payments_sell:
            transaction = self.mapper.from_fiat_payments(item, 1)
            self.add_transaction(transaction)

        self.session.commit()

        print("FIAT PAYMENTS: DONE")

    def _import_trade_flow_single_day(self, dt: datetime):
        print(f"TRADE FLOW: {dt.date().isoformat()}")

        trade_flow = self.api.convert_trade_flow(
            start_dt=dt,
            end_dt=dt + timedelta(days=1, milliseconds=-1),
        )

        for item in trade_flow:
            transaction = self.mapper.from_trade_flow(item)
            self.add_transaction(transaction)

        self.session.commit()

    def import_trade_flow(self):
        print("TRADE FLOW: START")

        for dt in rrule(DAILY, dtstart=self.start_date, until=self.end_date):
            self._import_trade_flow_single_day(dt)

        print("TRADE FLOW: DONE")

    def _import_symbol_trades(self, symbol: dict):
        print(f"MY TRADES: {symbol['symbol']}")

        symbol_trades = self.api.my_trades(symbol["symbol"])
        for item in symbol_trades:
            transaction = self.mapper.from_my_trades(symbol, item)
            self.add_transaction(transaction)

        self.session.commit()

    def import_my_trades(self):
        print("MY TRADES: START")

        exchange_info = self.api.exchange_info()

        for symbol in exchange_info["symbols"]:
            self._import_symbol_trades(symbol)
        self.session.commit()

        print("MY TRADES: DONE")

    def run(self):
        print("EXCHANGE IMPORT: START")

        try:
            self.import_withdraw_history()
            self.import_asset_dividends()
            self.import_asset_dribblets()
            self.import_fiat_orders()
            self.import_fiat_payments()
            self.import_trade_flow()
            self.import_my_trades()
        finally:
            self.session.close()
            self.api.session.close()

        print("EXCHANGE IMPORT: DONE")
