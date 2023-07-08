from starlette import status
from pydantic import BaseModel, Field
from fastapi import HTTPException, APIRouter

from models import User
from dependencies import user_dependency, db_dependency_type, bcrypt_context


router = APIRouter(
    prefix='/user',
    tags=['user']
)


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/')
async def get_user(user: user_dependency, db: db_dependency_type):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    return db.query(User.id == user.get('id')).first()


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency_type, user_verification: UserVerification):
    if User is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()
