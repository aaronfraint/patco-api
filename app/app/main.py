import os
from dotenv import find_dotenv, load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .options import Direction, Station, RouteEndpoint
from .database import sql_query_raw, postgis_query_to_geojson
from .utils import get_current_time_est, get_day_of_week, what_direction_is_this

from .queries.geoms import GET_STATION_GEOMS
from .queries.timetable import GET_TIMES_FOR_SINGLE_STATION, GET_TIMES_FOR_TWO_STATIONS


load_dotenv(find_dotenv())

URL_PREFIX = os.getenv("URL_PREFIX", "/api/v0")

app = FastAPI(docs_url=URL_PREFIX)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def get_api_status():
    return {
        "status": f"running via automated deployment at {URL_PREFIX}",
        "current_time": get_current_time_est(),
    }


@app.get(URL_PREFIX + "/station-geoms/")
async def get_station_geoms():
    query, columns = GET_STATION_GEOMS()
    return await postgis_query_to_geojson(query, columns)


@app.get(URL_PREFIX + "/timetable/")
async def timetable_for_station(
    station_name: Station,
    direction: Direction,
):
    current_time = get_current_time_est().time()
    tablename = f"timetable_{get_day_of_week()}_{direction}"

    query = GET_TIMES_FOR_SINGLE_STATION(station_name, tablename, current_time)

    times = await sql_query_raw(query)

    return {
        "source_table": tablename,
        "for_station": station_name,
        "times_after": current_time,
        "upcoming_times": times,
    }


@app.get(URL_PREFIX + "/trip-options/")
async def trip_options(
    origin_station_name: Station,
    destination_station_name: Station,
    time: str,
    arrive_or_depart: RouteEndpoint,
    limit: int = 10,
):
    direction = what_direction_is_this(origin_station_name, destination_station_name)

    tablename = f"timetable_{get_day_of_week()}_{direction}"

    query = GET_TIMES_FOR_TWO_STATIONS(
        origin_station_name,
        destination_station_name,
        tablename,
        time,
        arrive_or_depart,
        limit,
    )

    times = await sql_query_raw(query)

    return {
        "source_table": tablename,
        "origin": origin_station_name,
        "destination": destination_station_name,
        "direction": direction,
        "arrive_or_depart": arrive_or_depart,
        "time": time,
        "upcoming_times": times,
    }
