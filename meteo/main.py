# uvicorn main:app --reload --port 8200
from numbers import Number

import requests
from uuid import uuid4

from fastapi import FastAPI, Request, HTTPException
from sqlalchemy import Column, MetaData, Integer, create_engine, DateTime, func
from sqlalchemy.engine import ObjectKind
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import Identity
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import insert
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float

from models import CityModel, City

engine = create_engine('postgresql+psycopg2://localhost:5432/streamway')

Base = declarative_base()

metadata = MetaData()

# meteo_table = Table(
#     "meteo",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("min", Integer),
#     Column("max", Integer),
#     Column("createdAt", String),
# )


#debug
# with Session(engine) as session:
#     # cursor = conn.execution_options(stream_results=True).execute(text("select * from users"))
#     # data = cursor.fetchall()
#     # print(data)
#     # stmt = select(Meteo).where(Meteo.id == 2) #  SELECT meteo.id, meteo.min, meteo.max, meteo."createdAt" FROM meteo WHERE id == 2where(Meteo.id == 2) #  SELECT meteo.id, meteo.min, meteo.max, meteo."createdAt" FROM meteo WHERE id == 2
#     stmt = select(Meteo) # SELECT meteo.id, meteo.min, meteo.max, meteo."createdAt" FROM meteo WHERE id == 2where(Meteo.id == 2) #  SELECT meteo.id, meteo.min, meteo.max, meteo."createdAt" FROM meteo
#     result = session.scalars(stmt).all()
#     #
#     # data = session.query(meteo_table).all()
#     #
#     # print('stmt', result)
#
#     for meteo in result:
#         print(f"User: {meteo.id} MAX: {meteo.max}")
#
#     # result = insert(Meteo).values(id=3, min=3, max=33)
#     # do_nothing_stmt = result.on_conflict_do_nothing(index_elements=["id"])
#     # print(do_nothing_stmt)
#
#     new_meteo = Meteo(min=4, max=44)
#     session.add(new_meteo)
#     session.commit()
#     session.close()


# lat = [40.1811,51.5085,43.7064]

def get_url(cities):
    # lat = [40.1811]
    # lon = [44.5136]
    lat = []
    lon = []

    for city in cities:
        lat.append(city.lat)
        lon.append(city.lon)

    lat_parse = ",".join([str(num) for num in lat])
    lon_parse = ",".join([str(num) for num in lon])
    url = ""
    return url


def get_meteo_items():
    with Session(engine) as session:
        stmt = select(Meteo)
        result = session.scalars(stmt).all()

        for meteo in result:
            print(f"Meteo item: {meteo.id} MAX: {meteo.max}")

        new_meteo = Meteo(min=4, max=44)
        session.add(new_meteo)
        session.commit()
        session.close()


# add Meteo debug
# def add_meteo_items():
#     with Session(engine) as session:
#         new_meteo = Meteo(min=4, max=44)
#         session.add(new_meteo)
#         session.commit()
#         session.close()



# app = FastAPI(app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False}))
app = FastAPI()
#
@app.get("/meteo")
def meteo():
        return "test - ok!"


class Item(BaseModel):
    text1: str
    text2: str

# @app.post("/meteo/add")
# def meteo(item: Item):
#     print('add:', item)
#     add_meteo_items()
#     return 'added'


def fetch_meteo_data():
    try:
        # TODO: need check is City includes in lat lon
        cities = get_cities()
        url = get_url(cities)
        response = requests.get(url)  # Replace with your FastAPI endpoint
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=f"open-meteo Api: {e}")


# Meteo
class Meteo(BaseModel):
    min: int
    max: int
    description: str
    cityId: int

class MeteoModel(Base):
    __tablename__ = 'meteo_temps'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    min = Column(Integer)
    max = Column(Integer)
    created = Column(DateTime)
    cityId = Column(Integer)



def set_meteo_data():

    # Insert multiple records
    # session = Session()
    # users = [
    #     User(name='Alice', email='alice@example.com'),
    #     User(name='Bob', email='bob@example.com'),
    #     User(name='Carol', email='carol@example.com')
    # ]
    # session.add_all(users)
    # session.commit()
    # session.close()

    session = Session(engine)

    try:
        cities = get_cities()
        url = get_url(cities)
        response = requests.get(url)
        print(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        resp = response.json()

        data = []

        if type(resp) is dict:
            data.append(resp)
        else:
            data = resp

        for idx_city in range(len(data)):
            minTemps = data[idx_city]['daily']['temperature_2m_min']
            maxTemps = data[idx_city]['daily']['temperature_2m_max']
            timestamps = data[idx_city]['daily']['time']
            print(type(minTemps))

            new_temps = []

            for idx_temp in range(len(minTemps)):
                min = minTemps[idx_temp]
                max = maxTemps[idx_temp]
                temp = MeteoModel(min=min, max=max, cityId=cities[idx_city].id, created=timestamps[idx_temp])
                new_temps.append(temp)

            session.add_all(new_temps)
            session.commit()
            session.close()


        return 'done'
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=f"open-meteo Api: {e}")

#Meteo
@app.get("/meteo/update")
def fetch():
    return set_meteo_data()

@app.get("/meteo/data")
def test():
    return fetch_meteo_data()

# get cities
@app.get("/meteo/city/get")
def get_cities():
    try:
        with Session(engine) as session:
            cities =  session.query(CityModel).all()
            return cities
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

# add city
@app.post("/meteo/city/add")
def add_city(body: City):
    try:
        with Session(engine) as session:
            # new_city = CityModel(city = body.city, country = body.country, lat = body.lat, lon = body.lon, description = body.description)
            new_city = CityModel(**body.model_dump())
            session.add(new_city)
            session.commit()
            session.close()
        return "added"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    raise HTTPException(status_code=500, detail=f"open-meteo Api: {e}")
