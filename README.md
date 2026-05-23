# Pereval REST API

## Описание проекта

REST API для ведения базы данных горных перевалов. Проект разработан в рамках курса SkillFactory.

API позволяет мобильному приложению отправлять данные о горных перевалах на сервер, получать информацию о ранее добавленных объектах и редактировать их (при определенных условиях).

## Функциональность

- Добавление информации о новых перевалах
- Получение информации о перевале по его ID
- Получение списка перевалов, отправленных пользователем по email
- Редактирование существующих записей (только в статусе "new")
- Автоматическая документация через Swagger

## Технологии

- **Python 3.8+**
- **FastAPI** - веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **PostgreSQL** - реляционная база данных
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер

## Структура проекта
pereval_project/
├── config.py # Конфигурация БД из переменных окружения
├── models.py # Модели таблиц базы данных
├── main.py # REST API и класс PerevalManager
├── requirements.txt # Зависимости проекта
├── .env # Переменные окружения (не в git)
└── README.md # Документация
## Установка и запуск

### Предварительные требования

- Python 3.8 или выше
- PostgreSQL 12+
- pip (менеджер пакетов Python)

### 1. Клонирование репозитория

```bash
git clone https://github.com/pirat13-NIK/pereval_submit.git
cd pereval_submit


2. Установка зависимостей


pip install -r requirements.txt


3. Настройка базы данных

Создайте базу данных в PostgreSQL:
CREATE DATABASE fstr_db;

4. Настройка переменных окружения

Создайте файл .env в корне проекта:
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=postgres
FSTR_DB_PASS=your_password
FSTR_DB_NAME=fstr_db

5. Запуск сервера

uvicorn main:app --reload
Сервер запустится по адресу: http://localhost:8000

Документация API
Swagger UI доступен после запуска по адресу: http://localhost:8000/docs

Методы API
POST /submitData
Добавление информации о новом перевале.

Пример запроса:

json
{
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "test@mail.ru",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович",
    "phone": "+7 999 123 45 67"
  },

  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },

  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },

  "images": [
    {
      "data": "base64_image_data",
      "title": "Седловина"
    }
  ]
}
Успешный ответ (200):
{
  "status": 200,
  "message": null,
  "id": 1
}
GET /submitData/{id}
Получение информации о перевале по ID.

Пример запроса: GET /submitData/1

Успешный ответ (200):
{
  "id": 1,
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "status": "new",
  "user": {
    "email": "test@mail.ru",
    "fam": "Иванов",
    "name": "Иван"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А"
  },
  "images": [...]
}
GET /submitData/?user__email={email}
Получение всех перевалов пользователя.

Пример запроса: GET /submitData/?user__email=test@mail.ru

Успешный ответ (200):
{
  "status": 200,
  "message": null,
  "data": [
    {
      "id": 1,
      "title": "Пхия",
      "status": "new"
    }
  ]
}
PATCH /submitData/{id}
Обновление перевала (только в статусе "new").

Важно: Нельзя редактировать ФИО, email и телефон пользователя.

Пример запроса: PATCH /submitData/1

Успешный ответ:
{
  "state": 1,
  "message": null
}
Ошибка (статус не new):
{
  "state": 0,
  "message": "Нельзя редактировать перевал в статусе 'accepted'"
}
Структура базы данных
Таблицы
users - пользователи

email (уникальный)

phone, fam, name, otc

coords - координаты

latitude, longitude, height

levels - уровни сложности

winter, summer, autumn, spring

pereval_added - перевалы

beauty_title, title, other_titles

status (new/pending/accepted/rejected)

связи с users, coords, levels

pereval_images - изображения

data (base64), title

Класс PerevalManager
Основной класс для работы с базой данных содержит методы:

add_pereval(data) - добавление нового перевала

get_pereval_by_id(id) - получение перевала по ID

get_pereval_by_email(email) - получение перевалов пользователя

update_pereval(id, data) - обновление перевала

_format_pereval_response(pereval) - форматирование ответа

Переменные окружения
Проект использует следующие переменные окружения:

Переменная	Описание	По умолчанию
FSTR_DB_HOST	Хост БД	localhost
FSTR_DB_PORT	Порт БД	5432
FSTR_DB_LOGIN	Логин БД	postgres
FSTR_DB_PASS	Пароль БД	postgres
FSTR_DB_NAME	Имя БД	fstr_db
Git Workflow
Разработка велась по Git Flow:

main - стабильная версия

submitData - базовая функциональность

feature/get-patch-endpoints - дополнительные методы

docs/readme - документация

Тестирование
Для запуска тестов:
pytest test_main.py -v