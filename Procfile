release: alembic upgrade head
web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker coin_tracker.main:app
