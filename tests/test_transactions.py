import random

from faker import Faker
from fastapi import status

fake = Faker()


def test_list_transactions(user_client):
    expected = len([t for p in user_client.user.portfolios for t in p.transactions])
    response = user_client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == expected


def test_create_transaction(user_client):
    portfolio = random.choice(user_client.user.portfolios)

    data = {
        "portfolio_id": portfolio.id,
        "transaction_type": "trade",
        "transaction_date": "2022-01-01 00:00:00.000000",
        "buy_asset": fake.cryptocurrency_code(),
        "buy_amount": "1",
        "sell_asset": fake.cryptocurrency_code(),
        "sell_amount": "100",
        "fee_asset": fake.cryptocurrency_code(),
        "fee_amount": "0.01",
        "note": "test_create_transaction",
    }

    response = user_client.post("/transactions", json=data)
    assert response.status_code == status.HTTP_201_CREATED


def test_create_transaction_not_found(user_client, db_portfolios):
    portfolio_id = max([p.id for p in db_portfolios]) + 1

    data = {
        "portfolio_id": portfolio_id,
        "transaction_type": "trade",
        "transaction_date": "2022-01-01 00:00:00.000000",
        "buy_asset": fake.cryptocurrency_code(),
        "buy_amount": "1",
        "sell_asset": fake.cryptocurrency_code(),
        "sell_amount": "100",
        "fee_asset": fake.cryptocurrency_code(),
        "fee_amount": "0.01",
        "note": "test_create_transaction",
    }
    expected = f"Portfolio with id={portfolio_id} not found"

    response = user_client.post("/transactions", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == expected


def test_create_transaction_forbidden(user_client, db_portfolios):
    portfolio = random.choice([p for p in db_portfolios if p.user != user_client.user])

    data = {
        "portfolio_id": portfolio.id,
        "transaction_type": "trade",
        "transaction_date": "2022-01-01 00:00:00.000000",
        "buy_asset": fake.cryptocurrency_code(),
        "buy_amount": "1",
        "sell_asset": fake.cryptocurrency_code(),
        "sell_amount": "100",
        "fee_asset": fake.cryptocurrency_code(),
        "fee_amount": "0.01",
        "note": "test_create_transaction",
    }

    response = user_client.post("/transactions", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_single_transaction(user_client):
    portfolio = random.choice(user_client.user.portfolios)
    transaction = random.choice(portfolio.transactions)

    response = user_client.get(f"/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_200_OK


def test_get_single_transaction_not_found(user_client, db_transactions):
    transaction_id = max([t.id for t in db_transactions]) + 1

    response = user_client.get(f"/transactions/{transaction_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_single_transaction_forbidden(user_client, db_transactions):
    transaction = random.choice(
        [t for t in db_transactions if t.portfolio.user != user_client.user]
    )

    response = user_client.get(f"/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_transaction(user_client):
    portfolio = random.choice(user_client.user.portfolios)
    transaction = random.choice(portfolio.transactions)

    response = user_client.delete(f"/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Transaction removed successfully."


def test_delete_transaction_not_found(user_client, db_transactions):
    transaction_id = max([t.id for t in db_transactions]) + 1

    response = user_client.delete(f"/transactions/{transaction_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_transaction_forbidden(user_client, db_transactions):
    transaction = random.choice(
        [t for t in db_transactions if t.portfolio.user != user_client.user]
    )

    response = user_client.delete(f"/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
