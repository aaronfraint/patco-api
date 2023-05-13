from datetime import datetime
from pytz import timezone
from .options import STATIONS_EB


def get_current_time_est():
    return datetime.now(timezone("US/Eastern"))


def get_day_of_week():
    now = get_current_time_est().weekday()
    if now < 5:
        return "weekday"
    elif now == 5:
        return "saturday"
    elif now == 6:
        return "sunday"


def what_direction_is_this(start_station: str, end_station: str) -> str:
    start_index = STATIONS_EB.index(start_station)
    end_index = STATIONS_EB.index(end_station)

    if start_index < end_index:
        return "eb"
    else:
        return "wb"
