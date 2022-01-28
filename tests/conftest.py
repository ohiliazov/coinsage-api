from datetime import datetime
import random

import faker
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session

from coinsage.security import get_password_hash, create_access_token
from coinsage.config import settings
from coinsage.constants import TransactionType
from coinsage.main import app
from coinsage.dependencies import get_db_session
from coinsage.models import SQLModel, User, Portfolio, Transaction

test_engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

fake = faker.Faker()


class UserClient(TestClient):
    def __init__(self, *args, user: User = None, access_token: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if access_token:
            self.headers.update({"Authorization": f"Bearer {access_token}"})


def get_db_session_override():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_db_session] = get_db_session_override


@pytest.fixture
def db_session() -> Session:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield from get_db_session_override()


@pytest.fixture
def db_users(db_session) -> list[User]:
    users = []
    for _ in range(2):
        username = fake.user_name()
        user = User(
            username=username,
            password=get_password_hash(username),
        )
        for _ in range(2):
            portfolio = Portfolio(name=fake.sentence(3))
            for _ in range(2):
                transaction = Transaction(
                    transaction_type=TransactionType.TRADE,
                    transaction_date=datetime.utcnow(),
                    buy_asset="BTC",
                    buy_amount="1",
                    sell_asset="USD",
                    sell_amount="40000",
                    fee_asset="USD",
                    fee_amount="4",
                    note="40000 USD per BTC",
                )

                portfolio.transactions.append(transaction)
                db_session.add(transaction)

            user.portfolios.append(portfolio)
            db_session.add(portfolio)

        users.append(user)
        db_session.add(user)

    db_session.commit()

    for user in users:
        db_session.refresh(user)

    return users


@pytest.fixture
def db_portfolios(db_users) -> list[Portfolio]:
    return [db_portfolio for db_user in db_users for db_portfolio in db_user.portfolios]


@pytest.fixture
def db_transactions(db_portfolios) -> list[Transaction]:
    return [
        db_transaction
        for db_portfolio in db_portfolios
        for db_transaction in db_portfolio.transactions
    ]


@pytest.fixture
def test_client(db_session) -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture
def user_client(db_session, db_users) -> UserClient:
    user = random.choice(db_users)
    access_token = create_access_token({"sub": user.username})

    client = UserClient(app, user=user, access_token=access_token)

    return client
