from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlmodel import Session

from ..dependencies import get_db_session, get_current_user
from ..models import User, Portfolio, Transaction
from ..schemas.transactions import TransactionCreate, TransactionRead

router = APIRouter(tags=["portfolio"])


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    current_user: User = Depends(get_current_user),
):
    return [t for p in current_user.portfolios for t in p.transactions]


@router.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    portfolio = session.get(Portfolio, data.portfolio_id)

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id={data.portfolio_id} not found",
        )

    if portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    transaction = Transaction.from_orm(data)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_single_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    transaction = session.get(Transaction, transaction_id)

    if not transaction:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if transaction.portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return transaction


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    transaction = session.get(Transaction, transaction_id)

    if not transaction:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if transaction.portfolio.user != current_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    session.delete(transaction)
    session.commit()

    return {"detail": "Transaction removed successfully."}
