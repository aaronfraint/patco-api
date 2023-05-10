from datetime import datetime
from pytz import timezone

from .constants import STATION_NAMES


def get_current_time_est():
    return datetime.now(timezone("US/Eastern"))


def get_day_of_week():
    now = get_current_time_est().weekday()
    if now < 5:
        return "weekday"
    elif now == 5:
        return "satuday"
    elif now == 6:
        return "sunday"


def is_station_name(station_name: str):
    return station_name in STATION_NAMES
