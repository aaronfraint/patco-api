import os
from dotenv import find_dotenv, load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import sql_query_raw
from .utils import get_current_time_est, get_day_of_week
from .queries import get_times_for_single_station, get_times_for_two_stations
from .options import Direction, Station, RouteEndpoint

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


@app.get(URL_PREFIX + "/timetable/")
async def timetable_for_station(
    station_name: Station,
    direction: Direction,
):
    current_time = get_current_time_est().time()
    tablename = f"timetable_{get_day_of_week()}_{direction}"

    times = await get_times_for_single_station(station_name, tablename, current_time)

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
    direction: Direction,
    limit: int = 10,
):
    # TODO: figure out the `direction` within the code, based on start and end stations

    tablename = f"timetable_{get_day_of_week()}_{direction}"

    times = await get_times_for_two_stations(
        origin_station_name,
        destination_station_name,
        tablename,
        time,
        arrive_or_depart,
        limit,
    )

    return {
        "source_table": tablename,
        "origin": origin_station_name,
        "destination": destination_station_name,
        "arrive_or_depart": arrive_or_depart,
        "time": time,
        "upcoming_times": times,
    }
