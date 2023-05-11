import os
from dotenv import find_dotenv, load_dotenv
from enum import Enum

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import sql_query_raw
from .utils import get_current_time_est, get_day_of_week


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


class Direction(str, Enum):
    eb = "eb"
    wb = "wb"


class Station(str, Enum):
    x15_16th_and_locust = "15_16th_and_locust"
    x12_13th_and_locust = "12_13th_and_locust"
    x9_10th_and_locust = "9_10th_and_locust"
    x8th_and_market = "8th_and_market"
    city_hall = "city_hall"
    broadway = "broadway"
    ferry_ave = "ferry_ave"
    collingswood = "collingswood"
    westmont = "westmont"
    haddonfield = "haddonfield"
    woodcrest = "woodcrest"
    ashland = "ashland"
    lindenwold = "lindenwold"


class RouteEndpoint(str, Enum):
    arrive = "arrive"
    depart = "depart"


@app.get("/")
def get_api_status():
    return {
        "status": f"running via automated deployment at {URL_PREFIX}",
        "current_time": get_current_time_est(),
    }


# @app.get(URL_PREFIX + "/active-service-id/")
# async def active_service_id():
#     """
#     Get the service id for the current day.
#     Each of [Weekday, Saturday, Sunday] has its own ID.
#     """
#     now = get_current_time_est()
#     today = str(now.date()).replace("-", "")
#     day_of_week = get_day_of_week()
#     active_service_query = f"""
#         SELECT
#             service_id,
#             CASE
#                 WHEN sunday = 1 THEN 'Sunday'
#                 WHEN saturday = 1 THEN 'Saturday'
#                 ELSE 'Weekday'
#             END AS day_of_week
#         FROM calendar
#         WHERE end_date >= {today}
#     """

#     results = await sql_query_raw(active_service_query)

#     for entry in results:
#         if entry["day_of_week"] == day_of_week:
#             return {**entry, "time": now}


async def get_times_for_single_station(
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


async def get_times_for_two_stations(
    origin_station_name: str,
    destination_station_name: str,
    tablename: str,
    time: str,
    arrive_or_depart: str,
    limit: int,
):
    """
    Tablename encapsulates the day of week and direction
    Station name should be a sanitized, valid name of a PATCO station
    Time can be any current, past, or future time formatted as HH:MM:SS
    """

    # Build up the proper WHERE clause depending on the directionality requested
    if arrive_or_depart == "arrive":
        where_clause = f"""
            where destination_station::time <= '{time}'::time
            order by destination_station::time desc
            limit {limit}
        """
    elif arrive_or_depart == "depart":
        where_clause = f"""
            where origin_station::time >= '{time}'::time
            order by origin_station::time asc
            limit {limit}
        """

    query = f"""
        with _data as (
            select
                station_{origin_station_name} as origin_station,
                station_{destination_station_name} as destination_station
            from {tablename}
            where
                station_{origin_station_name} != 'Does not stop'
                and
                station_{destination_station_name} != 'Does not stop'
        )
        select origin_station, destination_station	
        from _data
        {where_clause}
    """

    print(query)

    result = await sql_query_raw(query)

    return [[x["origin_station"], x["destination_station"]] for x in result]


@app.get(URL_PREFIX + "/timetable/")
async def timetable_for_station(station_name: Station, direction: Direction):
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
