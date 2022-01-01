from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..dependencies import get_db_session, get_current_user
from ..models import User, Portfolio
from ..schemas.portfolios import PortfolioCreate, PortfolioRead
from ..schemas.transactions import TransactionRead

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio", response_model=list[PortfolioRead])
def list_portfolios(current_user: User = Depends(get_current_user)):
    return current_user.portfolios


@router.post(
    "/portfolio",
    response_model=PortfolioRead,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = Portfolio.from_orm(data, update={"user_id": current_user.id})

    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)

    return portfolio


@router.get("/portfolio/{portfolio_id}", response_model=PortfolioRead)
def get_single_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, portfolio_id)

    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return portfolio


@router.patch("/portfolio/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    portfolio_id: int,
    data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, portfolio_id)

    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    portfolio.name = data.name

    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)

    return portfolio


@router.delete("/portfolio/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, portfolio_id)

    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    session.delete(portfolio)
    session.commit()

    return {"detail": "Portfolio removed successfully."}


@router.get(
    "/portfolio/{portfolio_id}/transactions",
    response_model=list[TransactionRead],
)
def list_portfolio_transactions(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, portfolio_id)

    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return portfolio.transactions
