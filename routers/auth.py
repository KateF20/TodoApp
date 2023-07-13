from typing import Annotated
from datetime import timedelta, datetime

from starlette import status
from jose import jwt
from pydantic import BaseModel, Field, root_validator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from models import User
from dependencies import db_dependency_type, bcrypt_context, SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


class CreateUserModel(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    hashed_password: str = Field(...)

    @root_validator(pre=True)
    def password_hasher(cls, values):
        password = values.get('password')
        if password:
            hashed_password = bcrypt_context.hash(password)
            values['hashed_password'] = hashed_password
        return values


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM[0])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency_type, create_user_model: CreateUserModel):
    user_to_create = User(**create_user_model.dict(exclude={'password'}), is_active=True)

    db.add(user_to_create)
    db.commit()

    return user_to_create.username, user_to_create.hashed_password


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency_type):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not valid user')

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
