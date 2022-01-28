from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..dependencies import get_db_session, get_current_user
from ..models import User, Portfolio, Exchange
from ..schemas.exchanges import ExchangeCreate, ExchangeRead
from ..security import encrypt_data


router = APIRouter(tags=["exchages"])


@router.post(
    "/exchanges",
    response_model=ExchangeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_exchange_import(
    data: ExchangeCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, data.portfolio_id)

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id={data.portfolio_id} not found.",
        )

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    exchange = Exchange.from_orm(
        data,
        {
            "api_key": encrypt_data(data.api_key),
            "secret_key": encrypt_data(data.secret_key),
        },
    )

    session.add(exchange)
    session.commit()
    session.refresh(exchange)

    return exchange
