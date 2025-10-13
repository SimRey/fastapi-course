# Pydantic schema for Post
from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime
from pydantic.types import conint

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass # Inherits everything from PostBase


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        orm_mode = True  # To work with ORM objects directly


class UserOutSimple(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Post(PostBase):
    id: int
    created_at: datetime.datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True  # To work with ORM objects directly

class PostSimple(BaseModel):
    title: str
    content: str
    owner: UserOutSimple

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: PostSimple
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(ge=0, le=1)  # type: ignore # dir can only be 0 or 1