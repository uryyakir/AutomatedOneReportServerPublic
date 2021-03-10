from typing import Set
import datetime as dt
# custom modules
import os
import sys
# script will be run from /app directory
sys.path.append(os.path.abspath(os.getcwd()))  # adding app directory to path

from preform_requests import send_push_notification
from elastic_helpers.user_data_elastic_handler import Handlers
from config import constants


def get_users_with_missing_data() -> Set[str]:
    """get all users that have not yet filled in their data for next week"""
    users_data = {user["_source"]["VENDOR_UUID"] for user in Handlers.elastic_handler.get_all_today_data(
        _type="status",
        date_start=dt.date.today() + dt.timedelta(days=1),
        date_end=dt.date.today() + dt.timedelta(days=7),
    )}

    all_tokens = Handlers.token_handler.get_all_today_data(_type="token")
    to_dict = {dict_["_source"]["VENDOR_UUID"]: dict_["_source"]["TOKEN"] for dict_ in all_tokens}

    return set(dict(filter(lambda item_tup: item_tup[0] not in users_data, to_dict.items())).values())


if __name__ == "__main__":
    for token in get_users_with_missing_data():
        title, body = constants.APN.FILL_REPORT_REMINDER_STATUS
        send_push_notification.send_push(token, title=title, body=body)
