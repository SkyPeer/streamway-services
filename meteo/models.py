from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class City(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    description: str
    lastUpdated: str

class CityModel(Base):
    __tablename__ = 'forecast_cities'
    id = Column(Integer, primary_key=True)
    city = Column(String(100))
    country = Column(String(100))
    lat = Column(Float)
    lon = Column(Float)
    description = Column(String(255))
    lastUpdated = Column(String(255))

class Meteo(BaseModel):
    min: float
    max: float
    description: str
    cityId: int
    random: bool
    wind_speed: float
    wind_direction: float

class MeteoModel(Base):
    __tablename__ = 'forecast_temperature'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    min = Column(Float)
    max = Column(Float)
    predict = Column(Float)
    timeStamp = Column(DateTime)
    random = Column(Boolean)
    cityId = Column(Integer)
    wind_speed = Column(Float)
    wind_direction = Column(Float)

    __table_args__ = (
        # Unique constraint on pair of columns
        UniqueConstraint('min','max', 'cityId', name='created_cityId'),
    )
