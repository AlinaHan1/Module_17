from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session  # Сессия БД
from app.backend.db_depends import get_db  # Функция подключения к БД
from typing import Annotated  # Аннотации, Модели БД и Pydantic.
from app.models import Task, User
from app.schemas.task import CreateTask, UpdateTask
from app.schemas.user import CreateUser
from sqlalchemy import insert, select, update, delete  # Функции работы с записями.

from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])
DbSession = Annotated[Session, Depends(get_db)]


@router.get('/')
async def all_tasks(db: DbSession):
    """Получить список всех задач"""
    return db.scalars(select(Task)).all()


@router.get('/task_id')
async def task_by_id(db: DbSession, task_id: int):
    """Задача по идентификатору"""
    task = db.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
    return task


@router.post('/create')
async def create_task(db: DbSession, task_create: CreateTask, user_id: int):
    """Создать новую задачу"""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    db.execute(insert(Task).values(
        title=task_create.title,
        content=task_create.content,
        user_id=user_id,
        priority=task_create.priority,
        slug=slugify(task_create.title)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update_task')
async def update_task(db: DbSession, task_id: int, task_up: UpdateTask):
    """Обновить задачу"""
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
    db.execute(update(Task).where(Task.id == task_id).values(
        title=task_up.title,
        content=task_up.content,
        priority=task_up.priority,
        slug=slugify(task_up.title)))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task has been deleted'}


@router.delete('/delete')
async def delete_task(db: DbSession, task_id: int):
    """Удалить задачу"""
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task has been deleted'}
