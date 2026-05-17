from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from models import SessionLocal, User, Coords, Level, Pereval, PerevalImage


# Pydantic модели для валидации входных данных
class UserData(BaseModel):
    email: str
    fam: str = ""
    name: str = ""
    otc: str = ""
    phone: str = ""


class CoordsData(BaseModel):
    latitude: float
    longitude: float
    height: int


class LevelData(BaseModel):
    winter: str = ""
    summer: str = ""
    autumn: str = ""
    spring: str = ""


class ImageData(BaseModel):
    data: str
    title: str = ""


class PerevalRequest(BaseModel):
    beauty_title: str = ""
    title: str
    other_titles: str = ""
    connect: str = ""
    add_time: str
    user: UserData
    coords: CoordsData
    level: LevelData
    images: List[ImageData] = []


# КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
class PerevalManager:
    """
    Класс для добавления информации о перевалах в базу данных.
    """

    def __init__(self, db: Session):
        self.db = db

    def add_pereval(self, data: PerevalRequest) -> int:
        """
        Добавляет новый перевал со всей информацией.
        Возвращает ID созданного перевала.
        """
        # 1. Находим или создаём пользователя
        user = self.db.query(User).filter(User.email == data.user.email).first()
        if not user:
            user = User(
                email=data.user.email,
                phone=data.user.phone,
                fam=data.user.fam,
                name=data.user.name,
                otc=data.user.otc
            )
            self.db.add(user)
            self.db.flush()

        # 2. Создаём координаты
        coords = Coords(
            latitude=data.coords.latitude,
            longitude=data.coords.longitude,
            height=data.coords.height
        )
        self.db.add(coords)
        self.db.flush()

        # 3. Создаём уровень сложности
        level = Level(
            winter=data.level.winter,
            summer=data.level.summer,
            autumn=data.level.autumn,
            spring=data.level.spring
        )
        self.db.add(level)
        self.db.flush()

        # 4. Создаём перевал
        add_time = datetime.strptime(data.add_time, "%Y-%m-%d %H:%M:%S")
        pereval = Pereval(
            beauty_title=data.beauty_title,
            title=data.title,
            other_titles=data.other_titles,
            connect=data.connect,
            add_time=add_time,
            status='new',  # Устанавливаем статус "new"
            user_id=user.id,
            coord_id=coords.id,
            level_id=level.id
        )
        self.db.add(pereval)
        self.db.flush()

        # 5. Добавляем изображения
        for img in data.images:
            if img.data:
                image = PerevalImage(
                    data=img.data,
                    title=img.title,
                    pereval_id=pereval.id
                )
                self.db.add(image)

        # 6. Сохраняем всё в базу
        self.db.commit()

        # Возвращаем ID созданного перевала
        return pereval.id


# FastAPI приложение
app = FastAPI(title="Pereval API")


def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/submitData")
async def submit_data(data: PerevalRequest, db: Session = Depends(get_db)):
    """
    Метод для отправки данных о новом перевале.
    Принимает JSON с информацией о перевале.
    """
    try:
        # Проверяем обязательные поля
        if not data.title:
            return {
                "status": 400,
                "message": "Не указано название перевала",
                "id": None
            }

        if not data.user or not data.user.email:
            return {
                "status": 400,
                "message": "Не указан email пользователя",
                "id": None
            }

        # Создаём менеджер и добавляем перевал
        manager = PerevalManager(db)
        pereval_id = manager.add_pereval(data)

        return {
            "status": 200,
            "message": None,
            "id": pereval_id
        }

    except Exception as e:
        # Откатываем изменения при ошибке
        db.rollback()
        return {
            "status": 500,
            "message": f"Ошибка: {str(e)}",
            "id": None
        }


@app.get("/")
async def root():
    return {"message": "Pereval API работает"}