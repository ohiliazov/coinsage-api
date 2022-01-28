release: alembic upgrade head
web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker coinsage.main:app
