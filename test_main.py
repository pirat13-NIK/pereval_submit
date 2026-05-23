import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from models import Base
from config import DATABASE_URL

# Создаём тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём таблицы
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Переопределяем зависимость для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Тестовые данные
test_pereval = {
    "beauty_title": "пер. ",
    "title": "Тестовый перевал",
    "other_titles": "",
    "connect": "",
    "add_time": "2021-09-22 13:18:13",
    "user": {
        "email": "test@test.ru",
        "fam": "Тестов",
        "name": "Тест",
        "otc": "Тестович",
        "phone": "+7 999 123 45 67"
    },
    "coords": {
        "latitude": 45.3842,
        "longitude": 7.1525,
        "height": 1200
    },
    "level": {
        "winter": "1А",
        "summer": "1А",
        "autumn": "1А",
        "spring": ""
    },
    "images": [
        {
            "data": "test_image_data",
            "title": "Тестовое фото"
        }
    ]
}


def test_add_pereval():
    """Тест добавления нового перевала"""
    response = client.post("/submitData", json=test_pereval)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert data["id"] is not None
    return data["id"]


def test_get_pereval():
    """Тест получения перевала по ID"""
    # Сначала добавляем перевал
    pereval_id = test_add_pereval()

    # Получаем его по ID
    response = client.get(f"/submitData/{pereval_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Тестовый перевал"
    assert data["status"] == "new"
    assert data["user"]["email"] == "test@test.ru"


def test_get_pereval_by_email():
    """Тест получения перевалов по email"""
    response = client.get("/submitData/?user__email=test@test.ru")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert len(data["data"]) > 0


def test_update_pereval():
    """Тест обновления перевала"""
    # Добавляем новый перевал
    pereval_id = test_add_pereval()

    # Обновляем его
    update_data = test_pereval.copy()
    update_data["title"] = "Обновленный перевал"

    response = client.patch(f"/submitData/{pereval_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == 1

    # Проверяем, что обновление применилось
    response = client.get(f"/submitData/{pereval_id}")
    assert response.json()["title"] == "Обновленный перевал"


def test_update_pereval_wrong_status():
    """Тест обновления перевала с неправильным статусом"""
    # Добавляем перевал
    pereval_id = test_add_pereval()

    # Меняем статус напрямую
    db = TestingSessionLocal()
    from models import Pereval
    pereval = db.query(Pereval).filter(Pereval.id == pereval_id).first()
    pereval.status = "accepted"
    db.commit()
    db.close()

    # Пытаемся обновить
    response = client.patch(f"/submitData/{pereval_id}", json=test_pereval)
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == 0
    assert "Нельзя редактировать" in data["message"]


def test_validation():
    """Тест валидации"""
    invalid_data = test_pereval.copy()
    invalid_data["user"] = {"email": "", "fam": "", "name": "", "otc": "", "phone": ""}

    response = client.post("/submitData", json=invalid_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 400
    assert "Не указан email" in data["message"]