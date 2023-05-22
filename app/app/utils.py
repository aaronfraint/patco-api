from datetime import datetime
from pytz import timezone
from .options import STATIONS_EB


def get_current_datetime_est():
    return datetime.now(timezone("US/Eastern"))


def get_current_time():
    return get_current_datetime_est().time()


def get_day_of_week():
    today = get_current_datetime_est().weekday()
    if today < 5:
        return "weekday"
    elif today == 5:
        return "saturday"
    elif today == 6:
        return "sunday"


def what_direction_is_this(start_station: str, end_station: str) -> str:
    start_index = STATIONS_EB.index(start_station)
    end_index = STATIONS_EB.index(end_station)

    if start_index < end_index:
        return "eb"
    else:
        return "wb"
