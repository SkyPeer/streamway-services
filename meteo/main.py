# uvicorn main:app --reload --port 8200

import requests
import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from sqlalchemy.sql.expression import select
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from config import get_meteo_url, meteo_config

import pandas as pd
import psycopg2

conn = psycopg2.connect(database="streamway", user="", password="", host="localhost", port="5432")

# Read data from a table into a DataFrame

from datetime import datetime

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3039").split(",")

from models import CityModel, City, MeteoModel, Meteo

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
    start_date = '2025-08-10'
    end_date = '2025-08-22'

    url = get_meteo_url(start_date, end_date, lat_parse, lon_parse)

    print(url)
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
@app.get("/meteo/duplicates")
def meteo():
    # df = pd.read_sql("SELECT cityId, dt, count FROM meteo_temps WHERE count < 1 GROUP BY cityId, dt", conn)
    df = pd.read_sql("""WITH counts AS (SELECT  "cityId", created, COUNT(*) AS cnt FROM meteo_temps GROUP BY "cityId", created) SELECT "cityId", created, cnt FROM counts WHERE cnt > 1;""", conn)


    # Close the connection
    print(type(df)) # class 'pandas.core.frame.DataFrame'
    print(df)
    # df_to_list = df.values[1]
    # print('df_to_list', type(df_to_list))
    # conn.close()
    return len(df)

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
        # print(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        resp = response.json()

        # print(resp)

        data = []

        if type(resp) is dict:
            data.append(resp)
        else:
            data = resp

        for idx_city in range(len(data)):
            minTemps = data[idx_city][meteo_config["period"]][meteo_config["temp_min_pointer"]]
            maxTemps = data[idx_city][meteo_config["period"]][meteo_config["temp_max_pointer"]]
            windsSpeeds = data[idx_city][meteo_config["period"]][meteo_config["wind_speed_pointer"]]
            windsDirections = data[idx_city][meteo_config["period"]][meteo_config["wind_direction_pointer"]]
            timestamps = data[idx_city][meteo_config["period"]][meteo_config["time_pointer"]]
            print(type(minTemps))

            new_temps = []
            cityId = cities[idx_city].id

            # exists = session.query(MeteoModel).filter(MeteoModel.min == 27, MeteoModel.cityId == 1).exists()
            # print(exists, 'exists')
            #
            # if session.query(exists).scalar():
            #     print("User with this email already exists in department")

            for idx_temp in range(len(minTemps)):
                min = minTemps[idx_temp]
                max = maxTemps[idx_temp]
                wind_speed = windsSpeeds[idx_temp]
                wind_direction = windsDirections[idx_temp]
                date_string = timestamps[idx_temp]
                dt = datetime.strptime(date_string, "%Y-%m-%d")

                # ForeCasting

                # exsists = session.query(MeteoModel).filter(MeteoModel.cityId == cityId, MeteoModel.created == dt ).count() > 0

                temp = MeteoModel(min=min,
                                  max=max,
                                  cityId=cityId,
                                  timeStamp=dt,
                                  random=False,
                                  wind_speed = wind_speed,
                                  wind_direction = wind_direction)
                new_temps.append(temp)

                # if exsists:
                #     print('')
                # else:
                #     temp = MeteoModel(min=min, max=max, cityId=cityId, created=dt)
                #     new_temps.append(temp)

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


@app.get("/meteo/readings")
def get_readings_data():
    try:
        with Session(engine) as session:
            readings =  session.query(MeteoModel).all()
            return readings
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)