from datetime import timedelta, datetime

from sqlmodel import select, Session

from coin_tracker.dependencies import get_db_engine
from coin_tracker.importer.binance import BinanceImporter
from coin_tracker.models import Exchange
from coin_tracker.constants import ExchangeType
from coin_tracker.security import decrypt_data


def start_importer_daemon():
    with Session(get_db_engine()) as session:
        while True:
            current_date = datetime.utcnow()
            for exchange in session.exec(
                select(Exchange).where(
                    Exchange.exchange_type == ExchangeType.BINANCE
                )
            ).fetchall():
                importer = BinanceImporter(
                    session=session,
                    portfolio_id=exchange.portfolio_id,
                    api_key=decrypt_data(exchange.api_key),
                    secret_key=decrypt_data(exchange.secret_key),
                    start_date=current_date - timedelta(days=1),
                    end_date=current_date,
                )
                importer.run()
