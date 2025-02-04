from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from app.backend.db_depends import get_db  # Функция подключения к БД
from typing import Annotated  # Аннотации, Модели БД и Pydantic.
from app.models import User, Task
from app.schemas.user import CreateUser, UpdateUser
from app.schemas.task import CreateTask
from sqlalchemy import insert, select, update, delete  # Функции работы с записями.

from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get('/')
async def all_users(db: DbSession):
    """Получить список всех пользователей """
    return db.scalars(select(User)).all()


@router.get('/user_id')
async def user_by_id(db: DbSession, user_id: int):
    """Пользователь по идентификатору"""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    return user


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: DbSession, task_create: CreateTask, user_id: int):
    tasks = db.scalars(select(Task).where(User.id == user_id)).all()
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    return tasks


@router.post('/create')
async def create_user(user: CreateUser, db: DbSession) -> dict:
    """Создать нового пользователя"""
    db.execute(insert(User).values(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=slugify(user.username)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_user(db: DbSession, user_id: int, user_up: UpdateUser):
    """Обновить пользователя"""
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(
        firstname=user_up.firstname,
        lastname=user_up.lastname,
        age=user_up.age,
        slug=slugify(user_up.firstname)))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User has been deleted'}


@router.delete('/delete')
async def delete_user(db: DbSession, user_id: int):
    """Удалить пользователя"""
    user = db.scalar(select(User).where(User.id == user_id))
    tasks_delete = db.scalars(select(Task).where(Task.user_id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    db.execute(delete(User).where(User.id == user_id))
    if tasks_delete:
        db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User has been deleted'}
