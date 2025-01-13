from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Указание пути к базе данных (SQLite)
DATABASE_URL = "sqlite:///./taskmanager.db"

# Создание движка базы данных
engine = create_engine(DATABASE_URL, echo=True)

# Создание локальной сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass
