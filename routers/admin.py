from starlette import status
from fastapi import HTTPException, Path, APIRouter

from models import Todo

from dependencies import user_dependency, db_dependency_type

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.get('/todo')
async def get_all(user: user_dependency, db: db_dependency_type):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(Todo).all()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency_type, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo_to_delete = db.query(Todo).filter(Todo.id == todo_id).one_or_none()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
