import random

from faker import Faker
from fastapi import status

fake = Faker()


def test_list_portfolios(user_client):
    response = user_client.get("/portfolio")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(user_client.user.portfolios)


def test_create_portfolio(user_client):
    data = {"name": fake.sentence(3)}

    response = user_client.post("/portfolio", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == user_client.user.id


def test_get_single_portfolio(user_client):
    portfolio = random.choice(user_client.user.portfolios)

    response = user_client.get(f"/portfolio/{portfolio.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == portfolio.dict()


def test_get_single_portfolio_not_found(user_client, db_portfolios):
    portfolio_id = max(portfolio.id for portfolio in db_portfolios) + 1

    response = user_client.get(f"/portfolio/{portfolio_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_single_portfolio_forbidden(user_client, db_portfolios):
    portfolio = random.choice(
        [
            db_portfolio
            for db_portfolio in db_portfolios
            if db_portfolio.user != user_client.user
        ]
    )

    response = user_client.get(f"/portfolio/{portfolio.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_single_portfolio(user_client):
    portfolio = random.choice(user_client.user.portfolios)

    data = {"name": fake.sentence(3)}
    response = user_client.patch(f"/portfolio/{portfolio.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == data["name"]


def test_update_portfolio_not_found(user_client, db_portfolios):
    portfolio_id = max(portfolio.id for portfolio in db_portfolios) + 1

    data = {"name": fake.sentence(3)}
    response = user_client.patch(f"/portfolio/{portfolio_id}", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_portfolio_forbidden(user_client, db_portfolios):
    portfolio = random.choice(
        [
            db_portfolio
            for db_portfolio in db_portfolios
            if db_portfolio.user != user_client.user
        ]
    )

    data = {"name": fake.sentence(3)}
    response = user_client.patch(f"/portfolio/{portfolio.id}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_portfolio(user_client):
    portfolio = random.choice(user_client.user.portfolios)

    response = user_client.delete(f"/portfolio/{portfolio.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Portfolio removed successfully."

    response = user_client.get(f"/portfolio/{portfolio.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_portfolio_not_found(user_client, db_portfolios):
    portfolio_id = max(portfolio.id for portfolio in db_portfolios) + 1

    response = user_client.delete(f"/portfolio/{portfolio_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_portfolio_forbidden(user_client, db_portfolios):
    portfolio = random.choice(
        [
            db_portfolio
            for db_portfolio in db_portfolios
            if db_portfolio.user != user_client.user
        ]
    )

    response = user_client.delete(f"/portfolio/{portfolio.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_portfolio_transactions(user_client):
    portfolio = random.choice(user_client.user.portfolios)

    response = user_client.get(f"/portfolio/{portfolio.id}/transactions")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(portfolio.transactions)


def test_list_portfolio_transactions_not_found(user_client, db_portfolios):
    portfolio_id = max(portfolio.id for portfolio in db_portfolios) + 1

    response = user_client.get(f"/portfolio/{portfolio_id}/transactions")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_portfolio_transactions_forbidden(user_client, db_portfolios):
    portfolio = random.choice(
        [
            db_portfolio
            for db_portfolio in db_portfolios
            if db_portfolio.user != user_client.user
        ]
    )

    response = user_client.get(f"/portfolio/{portfolio.id}/transactions")
    assert response.status_code == status.HTTP_403_FORBIDDEN
