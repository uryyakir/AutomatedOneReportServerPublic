from typing import Tuple, Callable
import datetime as dt
from fastapi import status
# custom modules
from config.logger import logger


def get_legit_week_day(weekday: int) -> int:
    return (weekday + 2) % 8


def get_relevant_days() -> Tuple[dt.date, dt.date]:
    curr_date = dt.datetime.now().date()
    days_lst = []

    for i in range(0, 14 - get_legit_week_day(curr_date.weekday())):
        temp_date = curr_date + dt.timedelta(days=i)
        if get_legit_week_day(temp_date.weekday()) not in (6, 7):
            days_lst.append(temp_date)

    return min(days_lst), max(days_lst)


def api_tries(wrapped_function: Callable) -> Callable:
    def wrapper():
        try:
            wrapped_function()

        except:  # noqa
            logger.info("error in function")
            return status.HTTP_500_INTERNAL_SERVER_ERROR

    return wrapper
