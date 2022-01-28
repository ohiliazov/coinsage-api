import threading

from fastapi import FastAPI

from .database import engine
from .routes import auth, portfolios, transactions, exchanges
from .importer.daemon import start_importer_daemon


def run_daemon():
    task = threading.Thread(target=start_importer_daemon, daemon=True)
    task.start()


app = FastAPI(
    title="CoinSage - Portfolio Tracker",
    debug=True,
    on_startup=[engine.connect],
    on_shutdown=[engine.dispose],
    # on_startup=[run_daemon],
)
app.include_router(auth.router)
app.include_router(portfolios.router)
app.include_router(transactions.router)
app.include_router(exchanges.router)
