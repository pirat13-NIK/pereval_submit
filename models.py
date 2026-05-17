from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

# Подключение к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# Модели таблиц
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    fam = Column(String)
    name = Column(String)
    otc = Column(String)


class Coords(Base):
    __tablename__ = 'coords'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)


class Level(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True)
    winter = Column(String, default='')
    summer = Column(String, default='')
    autumn = Column(String, default='')
    spring = Column(String, default='')


class PerevalImage(Base):
    __tablename__ = 'pereval_images'
    id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)
    title = Column(String)
    pereval_id = Column(Integer, ForeignKey('pereval_added.id'))


class Pereval(Base):
    __tablename__ = 'pereval_added'
    id = Column(Integer, primary_key=True)
    beauty_title = Column(String)
    title = Column(String, nullable=False)
    other_titles = Column(String)
    connect = Column(String)
    add_time = Column(DateTime)
    status = Column(String, default='new')

    user_id = Column(Integer, ForeignKey('users.id'))
    coord_id = Column(Integer, ForeignKey('coords.id'))
    level_id = Column(Integer, ForeignKey('levels.id'))

    user = relationship("User")
    coord = relationship("Coords")
    level = relationship("Level")
    images = relationship("PerevalImage")


# Создание таблиц
Base.metadata.create_all(bind=engine)