import requests
from random import choices
from string import ascii_letters
import json
import datetime as dt
from pprint import pformat
from typing import Dict, List, Any, Tuple, Set, Union
# custom modules
import os
import sys
# script will be run from /app directory
sys.path.append(os.path.abspath(os.getcwd()))  # adding app directory to path

from config import constants
from config.logger import logger
from elastic_helpers.user_data_elastic_handler import Handlers
from preform_requests import send_status_smtp
from preform_requests import send_push_notification


def generate_boundary(k: int = 16) -> str:
    return "".join(
        choices(
            "".join(list(ascii_letters) + [str(num) for num in range(10)]),
            k=k
        )
    )


class PreformRequest:
    @staticmethod
    def preform_user_request(data_source: Dict[str, str], all_cookies: List[Dict[str, Any]]) -> Tuple[requests.Response, Dict[str, Any], Dict[str, Any]]:
        boundary = generate_boundary()
        cookie = [cookie["_source"]["COOKIE_STRING"] for cookie in all_cookies if cookie["_source"]["VENDOR_UUID"] == data_source["VENDOR_UUID"]][0]

        if cookie == "apple-tester-cookie":
            response = requests.post("https://automated-one-report.club/get-apple-tester-response")
            return response, cookie, {}

        payload = f"------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"MainCode\"\r\n\r\n{data_source['MAIN_CODE']}\r\n------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name=\"SecondaryCode\"\r\n\r\n{data_source['SECONDARY_CODE']}\r\n------WebKitFormBoundary{boundary}--"
        cookies = {
            "AppCookie": cookie
        }
        headers = json.loads(constants.OnePratAPIConstants.REQUEST_HEADERS.replace("{boundary}", boundary))

        response = requests.post(url=constants.OnePratAPIConstants.URL, headers=headers, data=payload, cookies=cookies)
        return response, cookie, headers

    @staticmethod
    def log_and_email(all_users: Set[str], successful_users: Set[str]) -> None:
        if all_users == successful_users:
            mail_text = f"REPORT STATUS WAS SENT FOR {len(successful_users)}, ALL OF WHICH WERE SUCCESSFUL!"
            logger.info(f"{'*'*20}{mail_text}{'*'*20}")
            send_status_smtp.send(subject="preform_user_requests success!", mail_text=mail_text)

        else:
            mail_text = f"REPORT STATUS WAS ATTEMPTED TO BE SENT FOR {len(all_users)} USERS\nBUT ONLY {len(successful_users)} WERE SUCCESSFUL ({round(100*len(successful_users)/len(all_users), 2)}%)"
            logger.warning(f"{'*'*20}{mail_text}{'*'*20}")
            send_status_smtp.send(subject="preform_user_requests failure!", mail_text=mail_text)

    @staticmethod
    def send_APNS(users: List[Dict[str, Union[str, bool]]]) -> None:
        all_tokens = Handlers.token_handler.get_all_today_data(_type="token")
        to_dict = {dict_["_source"]["VENDOR_UUID"]: dict_["_source"]["TOKEN"] for dict_ in all_tokens}

        for user in users:
            try:
                user_token = to_dict[user["VENDOR_UUID"]]
                send_push_notification.send_report_success_status(user_token, success=user["success"])

            except KeyError:
                # user has probably not accepted app notifications
                pass

    @staticmethod
    def preform_requests(debug: bool = False) -> None:
        users_data = Handlers.elastic_handler.get_all_today_data(_type="status")
        all_cookies = Handlers.cookies_handler.get_all_today_data(_type="cookie")
        current_run_users = Handlers.settings_handler.get_all_today_data(_type="settings", hour=dt.datetime.now().strftime("%H:%M"))
        current_run_user_ids = [user_id["_source"]["VENDOR_UUID"] for user_id in current_run_users]
        current_run_users_data = [user_data for user_data in users_data if user_data["_source"]["VENDOR_UUID"] in current_run_user_ids]

        successful_users, all_users = set(), set()

        for user_data in current_run_users_data:
            data_source = user_data["_source"]
            all_users.add(data_source['VENDOR_UUID'])
            assert "MAIN_CODE" in data_source and "SECONDARY_CODE" in data_source and "VENDOR_UUID" in data_source
            response, cookie, headers = PreformRequest.preform_user_request(data_source, all_cookies)

            if str(response.status_code) == "200":
                logger.info(
                    f"successful report for:\n\tUUID: {data_source['VENDOR_UUID']}\n\tusing app cookie: {cookie}\n\tusing headers: {pformat(headers)}\ngot response: {response.status_code if not response.text else ': ' + str(response.text)}")
                successful_users.add(data_source['VENDOR_UUID'])

            else:
                logger.warning(
                    f"FAILURE IN REPORT FOR:\n\tUUID: {data_source['VENDOR_UUID']}\n\tusing app cookie: {cookie}\n\tusing headers: {pformat(headers)}\ngot response: {response.status_code if not response.text else ': ' + str(response.text)}")

        if all_users:  # only if there were users to preform requests for within this run
            PreformRequest.log_and_email(all_users, successful_users)

        if not debug:
            PreformRequest.send_APNS(
                [{"VENDOR_UUID": successful_user, "success": True} for successful_user in successful_users] +
                [{"VENDOR_UUID": unsuccessful_user, "success": False} for unsuccessful_user in all_users - successful_users]
            )


if __name__ == "__main__":
    if int((dt.datetime.today()).strftime('%w')) in (5, 6):  # Fridays and Saturdays
        if dt.datetime.now().strftime("%H:%M") == "08:15":
            # only sending `no report needed` email once
            send_status_smtp.send(subject="no report needed for today!")

    else:
        try:
            PreformRequest.preform_requests()

        except Exception as err:
            send_status_smtp.send(subject="failure running PreformRequest.preform_requests()!", mail_text=str(err))
