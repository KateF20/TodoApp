from starlette import status
from pydantic import BaseModel, Field
from fastapi import HTTPException, Path, APIRouter

from models import Todo
from dependencies import user_dependency, db_dependency_type


router = APIRouter()


class TodoModel(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get('/')
async def get_all_todos(user: user_dependency, db: db_dependency_type):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    return db.query(Todo).filter(Todo.id == user.get('id')).all()


@router.get('/todo/{todo_id}')
async def get_todo_by_id(user: user_dependency, db: db_dependency_type, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='todo not found')


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency_type, todo_model: TodoModel):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo = Todo(**todo_model.dict(), owner_id=user.get('id'))

    db.add(todo)
    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency_type,
                   todo_model: TodoModel,
                   todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    todo.title = todo_model.title
    todo.description = todo_model.description
    todo.priority = todo_model.priority
    todo.complete = todo_model.complete

    db.add(todo_model)
    db.commit()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency_type, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
