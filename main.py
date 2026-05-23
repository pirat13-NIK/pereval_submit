from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

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
            status='new',
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

        return pereval.id

    def get_pereval_by_id(self, pereval_id: int) -> Optional[Dict]:
        """
        Получить перевал по ID со всей информацией.
        """
        pereval = self.db.query(Pereval).filter(Pereval.id == pereval_id).first()
        if not pereval:
            return None

        return self._format_pereval_response(pereval)

    def get_pereval_by_email(self, email: str) -> List[Dict]:
        """
        Получить все перевалы пользователя по email.
        """
        perevals = (
            self.db.query(Pereval)
            .join(User)
            .filter(User.email == email)
            .all()
        )

        return [self._format_pereval_response(p) for p in perevals]

    def update_pereval(self, pereval_id: int, data: PerevalRequest) -> tuple:
        """
        Обновить перевал, если он в статусе 'new'.
        Возвращает (state, message).
        """
        pereval = self.db.query(Pereval).filter(Pereval.id == pereval_id).first()

        if not pereval:
            return 0, "Перевал не найден"

        if pereval.status != 'new':
            return 0, f"Нельзя редактировать перевал в статусе '{pereval.status}'. Редактирование доступно только для статуса 'new'"

        try:
            # Обновляем основные поля (НЕ ФИО, email, phone пользователя)
            if data.beauty_title:
                pereval.beauty_title = data.beauty_title
            if data.title:
                pereval.title = data.title
            if data.other_titles is not None:
                pereval.other_titles = data.other_titles
            if data.connect is not None:
                pereval.connect = data.connect
            if data.add_time:
                pereval.add_time = datetime.strptime(data.add_time, "%Y-%m-%d %H:%M:%S")

            # Обновляем координаты
            if data.coords:
                coord = self.db.query(Coords).filter(Coords.id == pereval.coord_id).first()
                if coord:
                    coord.latitude = data.coords.latitude
                    coord.longitude = data.coords.longitude
                    coord.height = data.coords.height

            # Обновляем уровень сложности
            if data.level:
                level = self.db.query(Level).filter(Level.id == pereval.level_id).first()
                if level:
                    level.winter = data.level.winter
                    level.summer = data.level.summer
                    level.autumn = data.level.autumn
                    level.spring = data.level.spring

            # Обновляем изображения (удаляем старые и добавляем новые)
            if data.images:
                # Удаляем старые изображения
                self.db.query(PerevalImage).filter(PerevalImage.pereval_id == pereval.id).delete()

                # Добавляем новые
                for img in data.images:
                    if img.data:
                        image = PerevalImage(
                            data=img.data,
                            title=img.title,
                            pereval_id=pereval.id
                        )
                        self.db.add(image)

            self.db.commit()
            return 1, None

        except Exception as e:
            self.db.rollback()
            return 0, str(e)

    def _format_pereval_response(self, pereval) -> Dict:
        """
        Форматирует ответ с полной информацией о перевале.
        """
        return {
            "id": pereval.id,
            "beauty_title": pereval.beauty_title,
            "title": pereval.title,
            "other_titles": pereval.other_titles,
            "connect": pereval.connect,
            "add_time": pereval.add_time.strftime("%Y-%m-%d %H:%M:%S") if pereval.add_time else None,
            "status": pereval.status,
            "user": {
                "id": pereval.user.id,
                "email": pereval.user.email,
                "fam": pereval.user.fam,
                "name": pereval.user.name,
                "otc": pereval.user.otc,
                "phone": pereval.user.phone
            } if pereval.user else None,
            "coords": {
                "latitude": pereval.coord.latitude,
                "longitude": pereval.coord.longitude,
                "height": pereval.coord.height
            } if pereval.coord else None,
            "level": {
                "winter": pereval.level.winter,
                "summer": pereval.level.summer,
                "autumn": pereval.level.autumn,
                "spring": pereval.level.spring
            } if pereval.level else None,
            "images": [
                {
                    "data": img.data,
                    "title": img.title
                } for img in pereval.images
            ]
        }


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
    """
    try:
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

        manager = PerevalManager(db)
        pereval_id = manager.add_pereval(data)

        return {
            "status": 200,
            "message": None,
            "id": pereval_id
        }

    except Exception as e:
        db.rollback()
        return {
            "status": 500,
            "message": f"Ошибка: {str(e)}",
            "id": None
        }


@app.get("/submitData/{pereval_id}")
async def get_pereval(pereval_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о перевале по ID.
    """
    manager = PerevalManager(db)
    result = manager.get_pereval_by_id(pereval_id)

    if not result:
        raise HTTPException(status_code=404, detail="Перевал не найден")

    return result


@app.get("/submitData/")
async def get_pereval_by_email(
        user__email: str = Query(..., description="Email пользователя"),
        db: Session = Depends(get_db)
):
    """
    Получить список перевалов, отправленных пользователем с указанным email.
    """
    manager = PerevalManager(db)
    result = manager.get_pereval_by_email(user__email)

    if not result:
        return {
            "status": 404,
            "message": f"Нет перевалов для пользователя с email {user__email}",
            "data": []
        }

    return {
        "status": 200,
        "message": None,
        "data": result
    }


@app.patch("/submitData/{pereval_id}")
async def update_pereval(
        pereval_id: int,
        data: PerevalRequest,
        db: Session = Depends(get_db)
):
    """
    Обновить информацию о перевале (только если статус 'new').
    Запрещено редактировать ФИО, email и телефон пользователя.
    """
    manager = PerevalManager(db)
    state, message = manager.update_pereval(pereval_id, data)

    return {
        "state": state,
        "message": message
    }


@app.get("/")
async def root():
    return {"message": "Pereval API работает"}