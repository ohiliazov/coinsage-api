from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
