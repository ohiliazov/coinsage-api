import random

from faker import Faker
from fastapi import status

fake = Faker()


def test_sign_up(test_client):
    data = {
        "username": fake.user_name(),
        "password": fake.password(),
    }

    response = test_client.post("/sign-up", json=data)
    assert response.status_code == status.HTTP_201_CREATED


def test_sign_up_duplicate_username(test_client, db_users):
    user = random.choice(db_users)
    data = {
        "username": user.username,
        "password": user.username,
    }

    response = test_client.post("/sign-up", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The username is already taken."


def test_sign_in(test_client, db_users):
    user = random.choice(db_users)
    data = {
        "username": user.username,
        "password": user.username,
    }
    response = test_client.post("/sign-in", data=data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_sign_in_invalid_username(test_client):
    data = {
        "username": fake.user_name(),
        "password": fake.user_name(),
    }
    response = test_client.post("/sign-in", data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


def test_sign_in_invalid_password(test_client, db_users):
    user = random.choice(db_users)
    data = {
        "username": user.username,
        "password": fake.password(),
    }
    response = test_client.post("/sign-in", data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"
