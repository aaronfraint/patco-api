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


@app.get(URL_PREFIX + "/station/")
async def stop_times_for_station(stop_id: int, headsign: str):
    headsign_options = ["Philadelphia", "Lindenwold"]
    if headsign not in headsign_options:
        return {"message": f"Headsign parameter must be one of: {headsign_options}"}

    query = f"""
        select arrival_time 
        from stop_times
        where trip_id in (
            select trip_id
            from trips
            where service_id = 78
            and trip_headsign = 'Philadelphia'
        )
        and stop_id = {stop_id}
        order by arrival_time 
    """

    result = await sql_query_raw(query)
    stop_data = await get_name_of_stop(stop_id)

    return {
        "at_stop": stop_data[0],
        "heading_towards": headsign,
        "arrival_times": [x["arrival_time"] for x in result],
    }
