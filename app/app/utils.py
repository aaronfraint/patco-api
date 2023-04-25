from datetime import datetime
from pytz import timezone


def get_current_time_est():
    return datetime.now(timezone("US/Eastern"))
