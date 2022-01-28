from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select, create_engine
from sqlalchemy.engine import Engine


from .security import decode_token
from .config import settings
from .models import User
from .database import engine

http_bearer = HTTPBearer(auto_error=False)


def get_db_session() -> Session:
    with Session(engine) as session:
        yield session


def get_access_token(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    if token:
        return token.credentials


def get_current_user(
    access_token: str = Depends(get_access_token),
    session: Session = Depends(get_db_session),
) -> Optional[User]:
    username = decode_token(access_token)["sub"]
    result = session.exec(select(User).where(User.username == username))
    return result.one_or_none()
