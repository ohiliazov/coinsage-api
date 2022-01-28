from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..dependencies import get_db_session, get_current_user
from ..models import User, Portfolio
from ..schemas.portfolios import (
    PortfolioCreate,
    PortfolioRead,
    PortfolioOverviewRead,
)
from ..schemas.transactions import TransactionRead

router = APIRouter(tags=["portfolio"])


def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Portfolio:
    portfolio = session.get(Portfolio, portfolio_id)

    if not portfolio:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return portfolio


@router.get("/portfolios", response_model=list[PortfolioRead])
def list_portfolios(current_user: User = Depends(get_current_user)):
    return current_user.portfolios


@router.post(
    "/portfolios",
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


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioRead)
def get_single_portfolio(portfolio: Portfolio = Depends(get_portfolio)):
    return portfolio


@router.patch("/portfolios/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    data: PortfolioCreate,
    portfolio: Portfolio = Depends(get_portfolio),
    session: Session = Depends(get_db_session),
):

    portfolio.name = data.name

    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)

    return portfolio


@router.delete("/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio: Portfolio = Depends(get_portfolio),
    session: Session = Depends(get_db_session),
):

    session.delete(portfolio)
    session.commit()

    return {"detail": "Portfolio removed successfully."}


@router.get(
    "/portfolios/{portfolio_id}/transactions",
    response_model=list[TransactionRead],
)
def list_portfolio_transactions(portfolio: Portfolio = Depends(get_portfolio)):
    return portfolio.transactions


@router.get(
    "/portfolios/{portfolio_id}/overview",
    response_model=list[PortfolioOverviewRead],
)
def get_portfolio_overview(portfolio: Portfolio = Depends(get_portfolio)):
    overview = defaultdict(Decimal)

    for transaction in portfolio.transactions:
        if transaction.buy_asset:
            overview[transaction.buy_asset] += transaction.buy_amount
        if transaction.sell_asset:
            overview[transaction.sell_asset] -= transaction.sell_amount
        if transaction.fee_asset:
            overview[transaction.fee_asset] -= transaction.fee_amount

    return [
        {"asset": asset, "amount": amount}
        for asset, amount in overview.items()
        if not amount.is_zero()
    ]
