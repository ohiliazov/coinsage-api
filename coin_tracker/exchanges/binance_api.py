from datetime import datetime, timedelta
import hmac
import hashlib
import time
import httpx
from retrying import retry
from urllib.parse import urlencode


def retry_on_too_many_requests(exc: Exception):
    if isinstance(exc, httpx.HTTPStatusError):
        print(exc.response.status_code)
        print(exc.response.json())
        return exc.response.status_code in [418, 429]
    return False


class BinanceAPI:
    def __init__(
        self,
        api_key: str = None,
        secret_key: str = None,
        base_url: str = "https://api.binance.com",
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = httpx.Client(
            base_url=base_url,
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
        )
        if self.api_key:
            self.session.headers["X-MBX-APIKEY"] = self.api_key

    @staticmethod
    def _get_timestamp(dt: datetime = None) -> int:
        if not dt:
            dt = datetime.now()
        return int(dt.timestamp() * 1000)

    def _get_signature(self, payload: dict):
        data = {
            key: value for key, value in payload.items() if value is not None
        }
        query_string = urlencode(data, True).replace("%40", "@")
        return hmac.new(
            key=self.secret_key.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def sign_payload(self, payload: dict = None):
        if payload is None:
            payload = {}
        payload["timestamp"] = self._get_timestamp()
        payload["recvWindow"] = 60000

        if self.secret_key:
            payload["signature"] = self._get_signature(payload)

        return urlencode(payload, True).replace("%40", "@")

    @retry(wait_fixed=60, retry_on_exception=retry_on_too_many_requests)
    def send_request(
        self,
        method,
        url,
        params: dict = None,
        sign_request: bool = True,
    ):
        params = params.copy() if params else {}
        if sign_request:
            payload = self.sign_payload(params)
        else:
            payload = params

        response = self.session.request(method, url, params=payload)
        response.raise_for_status()

        return response.json()

    def exchange_info(self):
        return self.send_request(
            "GET",
            "/api/v3/exchangeInfo",
            sign_request=False,
        )

    def account(self):
        return self.send_request("GET", "/api/v3/account")

    def asset_dribblets(self):
        response = self.send_request("GET", "/sapi/v1/asset/dribblet")

        return [
            item
            for data in response["userAssetDribblets"]
            for item in data["userAssetDribbletDetails"]
        ]

    def asset_dividends(self):
        response = self.send_request("GET", "/sapi/v1/asset/assetDividend")

        return response["rows"]

    def convert_trade_flow(
        self,
        start_dt: datetime = None,
        end_dt: datetime = None,
        limit: int = 1000,
    ):
        """Conversion History"""
        if end_dt is None:
            end_dt = datetime.utcnow()
        if start_dt is None:
            start_dt = end_dt - timedelta(days=30)

        time.sleep(1)
        response = self.send_request(
            "GET",
            "/sapi/v1/convert/tradeFlow",
            {
                "startTime": self._get_timestamp(start_dt),
                "endTime": self._get_timestamp(end_dt),
                "limit": limit,
            },
        )

        return response["list"]

    def _fiat_orders(
        self,
        page: int,
        transaction_type: int,
        begin_time: datetime = None,
        end_time: datetime = None,
        rows: int = 500,
    ):
        """Fiat Deposit/Withdraw History"""
        params = {
            "transactionType": transaction_type,
            "page": page,
            "rows": rows,
        }
        if begin_time:
            params["beginTime"] = self._get_timestamp(begin_time)
        if end_time:
            params["endTime"] = self._get_timestamp(end_time)

        response = self.send_request(
            "GET",
            "/sapi/v1/fiat/orders",
            params,
        )

        return response["data"]

    def fiat_orders(
        self,
        transaction_type: int,
        begin_time: datetime = None,
        end_time: datetime = None,
        rows: int = 500,
    ):
        """Fiat Deposit/Withdraw History"""
        page = 0
        orders = []

        while True:
            page += 1
            data = self._fiat_orders(
                page=page,
                transaction_type=transaction_type,
                begin_time=begin_time,
                end_time=end_time,
                rows=rows,
            )
            orders.extend(data)

            if len(data) < rows:
                return orders

    def _fiat_payments(
        self,
        page: int,
        transaction_type: int,
        begin_time: datetime = None,
        end_time: datetime = None,
        rows: int = 500,
    ):
        """Fiat Payments History"""
        params = {
            "transactionType": transaction_type,
            "page": page,
            "rows": rows,
        }
        if begin_time:
            params["beginTime"] = self._get_timestamp(begin_time)
        if end_time:
            params["endTime"] = self._get_timestamp(end_time)

        response = self.send_request(
            "GET",
            "/sapi/v1/fiat/payments",
            params,
        )

        return response["data"]

    def fiat_payments(
        self,
        transaction_type: int,
        begin_time: datetime = None,
        end_time: datetime = None,
        rows: int = 500,
    ):
        """Fiat Payments History"""
        page = 0
        payments = []

        while True:
            page += 1
            data = self._fiat_payments(
                page=page,
                transaction_type=transaction_type,
                begin_time=begin_time,
                end_time=end_time,
                rows=rows,
            )
            payments.extend(data)

            if len(data) < rows:
                return payments

    def my_trades(self, symbol: str):
        """Trades history"""
        time.sleep(1)
        return self.send_request(
            "GET",
            "/api/v3/myTrades",
            {"symbol": symbol},
        )

    def ticker_price(self):
        return self.send_request("GET", "/api/v3/ticker/price")

    def deposit_history(self):
        return self.send_request("GET", "/sapi/v1/capital/deposit/hisrec")

    def withdraw_history(self):
        return self.send_request("GET", "/sapi/v1/capital/withdraw/history")
