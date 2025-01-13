from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete

router = APIRouter(prefix="/task", tags=["task"])


# Маршрут для получения всех задач
@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


# Маршрут для получения задачи по ID
@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        return task
    raise HTTPException(status_code=404, detail="Task was not found")


# Маршрут для создания задачи
@router.post("/create")
async def create_task(
    task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]
):
    # Проверка существования пользователя
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    # Добавление задачи
    stmt = insert(Task).values(
        title=task.title, content=task.content, priority=task.priority, user_id=user_id
    )
    db.execute(stmt)
    db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


# Маршрут для обновления задачи
@router.put("/update/{task_id}")
async def update_task(
    task_id: int, task: UpdateTask, db: Annotated[Session, Depends(get_db)]
):
    stmt = (
        update(Task)
        .where(Task.id == task_id)
        .values(title=task.title, content=task.content, priority=task.priority)
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Task update is successful!",
    }


# Маршрут для удаления задачи
@router.delete("/delete/{task_id}")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    stmt = delete(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task was not found")
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Task deletion is successful!",
    }
