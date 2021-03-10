from typing import Dict, List, Any, Optional, Union, cast
from fastapi import FastAPI, status, Request
import json
import datetime as dt
from copy import deepcopy
from starlette.templating import _TemplateResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
# import uvicorn
# custom modules
from elastic_helpers.user_data_elastic_handler import Handlers
from API_data_models import UserData, UserCookie, UserUUID, TokenUUID, UserSettings, IAPBuyer
from helpers import helpers
from config import constants

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class UserDataAPIHandler:
    """
    user data JSONs will look like that:
    {
        "VENDOR_UUID": "...",
        "DATE": 01/01/2020,
        "MAIN_CODE": "...",
        "TEXT": "...",
        "SECONDARY_CODE": "...",
        "SECONDARY_TEXT": "..."
    }
    """

    @staticmethod
    @helpers.api_tries
    @app.post("/index-user-data")
    async def index_user_data(request: UserData) -> int:
        request_data = json.loads(request.json())
        Handlers.elastic_handler.index_user_data(_type="status", data_json=request_data)
        return status.HTTP_200_OK

    @staticmethod
    @helpers.api_tries
    @app.post("/get-user-data")
    async def get_user_data(request: UserUUID) -> List[Dict[str, Any]]:
        request_data = json.loads(request.json())
        data = Handlers.elastic_handler.get_user_data(_type="status", vendor_uuid=request_data["VENDOR_UUID"])
        return data

    @staticmethod
    @helpers.api_tries
    @app.post("/index-user-cookie")
    async def index_user_cookie(request: UserCookie) -> int:
        request_data = json.loads(request.json())
        Handlers.cookies_handler.index_user_data(_type="cookie", data_json=request_data)
        return status.HTTP_200_OK

    @staticmethod
    @helpers.api_tries
    @app.post("/get-user-cookie-availability")
    async def get_user_cookie_availability(request: UserUUID) -> Optional[Dict[str, bool]]:
        request_data = json.loads(request.json())
        vendor_uuid = request_data["VENDOR_UUID"]
        data = Handlers.cookies_handler.get_user_data(_type="cookie", vendor_uuid=vendor_uuid)
        if not data:
            return {"exists": False}

        elif len(data) > 1:
            Handlers.cookies_handler.delete_old_status(vendor_uuid=vendor_uuid, curr_date=None)
            return {"exists": False}

        elif len(data) == 1:
            return {"exists": not dt.datetime.strptime(data[0]["_source"]["COOKIE_EXPIRY_DATE"], "%Y-%m-%dT%H:%M:%S").date() <= dt.datetime.now().date()}

        return None

    @staticmethod
    @helpers.api_tries
    @app.get("/scheduled-submission-hour")
    async def get_scheduled_submission_hour() -> Dict[str, int]:
        return {"scheduled_submission_hour": constants.OnePratAPIConstants.SCHEDULED_SUBMISSION_HOUR}

    @staticmethod
    @helpers.api_tries
    @app.get("/get-code-maps")
    async def get_code_maps() -> Dict[str, Dict[str, str]]:
        return constants.OnePratAPIConstants.CODE_MAP

    @staticmethod
    @helpers.api_tries
    @app.get("/get-outside-unit-options")
    async def get_outside_unit_options() -> Dict[str, List[str]]:
        return constants.OnePratAPIConstants.OUTSIDE_UNIT_OPTIONS

    @staticmethod
    @helpers.api_tries
    @app.get("/get-latest-version")
    async def get_latest_version() -> Dict[str, Union[str, bool]]:
        return {
            "latest_version": constants.AppVersion.LATEST_VERSION,
            "breaking_changes": constants.AppVersion.BREAKING_CHANGES,
            "should_notify": constants.AppVersion.SHOULD_NOTIFY
        }

    @staticmethod
    @helpers.api_tries
    @app.post("/index-user-token")
    async def index_user_token(request: TokenUUID) -> int:
        request_data = json.loads(request.json())
        Handlers.token_handler.index_user_data(_type="token", data_json=request_data)
        return status.HTTP_200_OK

    @staticmethod
    @helpers.api_tries
    @app.post("/get-user-settings")
    async def get_user_settings(request: UserUUID) -> Dict[str, Union[str, bool]]:
        request_data = json.loads(request.json())
        user_settings = cast(Dict[str, Union[str, bool]], Handlers.settings_handler.get_user_data(_type="settings", vendor_uuid=request_data["VENDOR_UUID"]))
        if not user_settings:
            defaults = cast(Dict[str, Union[str, bool]], deepcopy(constants.OnePratAPIConstants.DEFAULT_SETTINGS))
            defaults.update(constants.OnePratAPIConstants.POSSIBLE_REPORT_TIME)
            defaults["NEEDS_INDEXING"] = True
            return defaults

        user_settings.update(constants.OnePratAPIConstants.POSSIBLE_REPORT_TIME)
        user_settings["NEEDS_INDEXING"] = False
        return user_settings

    @staticmethod
    @helpers.api_tries
    @app.post("/index-user-settings")
    async def index_user_settings(request: UserSettings) -> int:
        request_data = json.loads(request.json())
        Handlers.settings_handler.index_user_data(_type="settings", data_json=request_data)
        return status.HTTP_200_OK

    @staticmethod
    @helpers.api_tries
    @app.post("/index-iap-buyer")
    async def index_iap_buyer(request: IAPBuyer) -> int:
        request_data = json.loads(request.json())
        Handlers.iap_buyers_handler.index_user_data(_type="iap_buyer", data_json=request_data)
        return status.HTTP_200_OK

    @staticmethod
    @helpers.api_tries
    @app.post("/is-iap-buyer")
    async def is_iap_buyer(request: UserUUID) -> Dict[str, Union[bool, List[str]]]:
        request_data = json.loads(request.json())
        iap_data = Handlers.iap_buyers_handler.get_user_data(_type="iap_buyers", vendor_uuid=request_data["VENDOR_UUID"])
        if iap_data:
            return {"eligible": True, "iap_purchased": list(set([data["_source"]["PRODUCT_ID"] for data in iap_data]))}

        else:
            return {"eligible": False, "iap_purchased": []}

    @staticmethod
    @helpers.api_tries
    @app.get("/get-apple-tester-response")
    async def get_apple_tester_response() -> int:
        return status.HTTP_200_OK

    @staticmethod
    @app.get("/support", response_class=HTMLResponse)
    async def support(request: Request) -> _TemplateResponse:
        return templates.TemplateResponse("support_page.html", {"request": request})

    @staticmethod
    @app.get("/privacy-policy", response_class=HTMLResponse)
    async def privacy_policy(request: Request) -> _TemplateResponse:
        return templates.TemplateResponse("privacy_policy.html", {"request": request})

    @staticmethod
    @app.get("/register", response_class=HTMLResponse)
    async def register(request: Request) -> _TemplateResponse:
        return templates.TemplateResponse("register_page.html", {"request": request})


# if __name__ == "__main__":
#     uvicorn.run(app, port=400)
