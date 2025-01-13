from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify
from fastapi.logger import logger

router = APIRouter(prefix="/user", tags=["user"])


# Маршрут для получения всех пользователей
@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


# Маршрут для получения пользователя по ID
@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        return user
    raise HTTPException(status_code=404, detail="User was not found")


# Маршрут для создания пользователя
@router.post("/create")
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    try:
        # Проверка на существование username
        existing_user = db.scalar(select(User).where(User.username == user.username))
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this username already exists."
            )

        # Генерация уникального slug
        base_slug = slugify(user.username)
        slug = base_slug
        counter = 1

        # Проверка уникальности slug
        while db.scalar(select(User).where(User.slug == slug)):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Добавление пользователя в базу
        stmt = insert(User).values(
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            age=user.age,
            slug=slug,
        )
        db.execute(stmt)
        db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while creating the user."
        )


# Маршрут для обновления пользователя
@router.put("/update/{user_id}")
async def update_user(
    user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]
):
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(firstname=user.firstname, lastname=user.lastname, age=user.age)
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User update is successful!",
    }


# Маршрут для удаления пользователя
@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Удаление задач пользователя
    db.execute(delete(Task).where(Task.user_id == user_id))

    # Удаление пользователя
    stmt = delete(User).where(User.id == user_id)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User was not found")
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User and related tasks deletion is successful!",
    }


# Маршрут для получения задач пользователя
@router.get("/{user_id}/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks
