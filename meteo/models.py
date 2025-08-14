from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class City(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    description: str
    lastUpdated: str

class CityModel(Base):
    __tablename__ = 'meteo_cities'
    id = Column(Integer, primary_key=True)
    city = Column(String(100))
    country = Column(String(100))
    lat = Column(Float)
    lon = Column(Float)
    description = Column(String(255))
    lastUpdated = Column(String(255))