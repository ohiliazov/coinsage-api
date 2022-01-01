import random
import faker

from fastapi import status

fake = faker.Faker()


def test_create_exchange(user_client):
    portfolio = random.choice(user_client.user.portfolios)
    data = {
        "portfolio_id": portfolio.id,
        "exchange_type": "binance",
        "api_key": fake.pystr(64, 64),
        "secret_key": fake.pystr(64, 64),
    }

    response = user_client.post("/exchanges", json=data)
    assert response.status_code == status.HTTP_201_CREATED


def test_create_exchange_not_found(user_client, db_portfolios):
    portfolio_id = max([p.id for p in db_portfolios]) + 1
    data = {
        "portfolio_id": portfolio_id,
        "exchange_type": "binance",
        "api_key": fake.pystr(64, 64),
        "secret_key": fake.pystr(64, 64),
    }

    response = user_client.post("/exchanges", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_exchange_forbidden(user_client, db_portfolios):
    portfolio = random.choice(
        [p for p in db_portfolios if p.user != user_client.user]
    )
    data = {
        "portfolio_id": portfolio.id,
        "exchange_type": "binance",
        "api_key": fake.pystr(64, 64),
        "secret_key": fake.pystr(64, 64),
    }

    response = user_client.post("/exchanges", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
