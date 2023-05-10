import os
from dotenv import find_dotenv, load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import sql_query_raw
from .utils import get_current_time_est, get_day_of_week
from .queries import get_name_of_stop

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


@app.get(URL_PREFIX + "/active-service-id/")
async def active_service_id():
    """
    Get the service id for the current day.
    Each of [Weekday, Saturday, Sunday] has its own ID.
    """
    now = get_current_time_est()
    today = str(now.date()).replace("-", "")
    day_of_week = get_day_of_week()
    active_service_query = f"""
        SELECT 
            service_id,
            CASE
                WHEN sunday = 1 THEN 'Sunday'
                WHEN saturday = 1 THEN 'Saturday'
                ELSE 'Weekday'
            END AS day_of_week
        FROM calendar
        WHERE end_date >= {today}    
    """

    results = await sql_query_raw(active_service_query)

    for entry in results:
        if entry["day_of_week"] == day_of_week:
            return {**entry, "time": now}


async def get_times(
    station_name: str,
    tablename: str,
    time: str,
):
    """
    Tablename encapsulates the day of week and direction
    Station name should be a sanitized, valid name of a PATCO station
    Time can be any current, past, or future time formatted as HH:MM:SS
    """
    query = f"""
        with _data as (
            select station_{station_name} as value
            from {tablename}
            where station_{station_name} != 'Does not stop'          
        )
        select
            value,
            value, value::time - '{time}'::time as seconds_away
        from _data
        where value::time >= '{time}'::time;
    """

    result = await sql_query_raw(query)

    return [[x["value"], x["seconds_away"]] for x in result]


@app.get(URL_PREFIX + "/timetable/")
async def timetable_for_station(station_name: str, direction: str = "wb"):
    names = [
        "15_16th_and_locust",
        "12_13th_and_locust",
        "9_10th_and_locust",
        "8th_and_market",
        "city_hall",
        "broadway",
        "ferry_ave",
        "collingswood",
        "westmont",
        "haddonfield",
        "woodcrest",
        "ashland",
        "lindenwold",
    ]
    if station_name not in names:
        return {"message": f"Station Name parameter must be one of: {names}"}

    current_time = get_current_time_est().time()
    tablename = f"timetable_{get_day_of_week()}_{direction}"

    times = await get_times(station_name, tablename, current_time)

    return {
        "source_table": tablename,
        "for_station": station_name,
        "times_after": current_time,
        "upcoming_times": times,
    }
