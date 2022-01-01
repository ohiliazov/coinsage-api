db_revision:
	alembic revision --autogenerate -m "$(name)"

db_upgrade:
	alembic upgrade head

db_downgrade:
	alembic downgrade -1

requirements:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
