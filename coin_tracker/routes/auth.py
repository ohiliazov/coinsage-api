from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session

from ..security import create_access_token, verify_password, get_password_hash
from ..dependencies import get_db_session
from ..schemas.auth import Token, UserCreate, UserRead
from ..models import User

router = APIRouter(tags=["auth"])


@router.post("/sign-in", response_model=Token)
async def sign_in(
    session: Session = Depends(get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    result = session.exec(
        select(User).filter(User.username == form_data.username).limit(1)
    )

    user: User
    if user := result.first():
        if verify_password(form_data.password, user.password):
            access_token = create_access_token({"sub": user.username})
            return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/sign-up",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    data: UserCreate,
    session: Session = Depends(get_db_session),
):
    result = session.exec(
        select(User).where(User.username == data.username).limit(1)
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The username is already taken.",
        )

    user = User.from_orm(data)
    user.password = get_password_hash(data.password)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
