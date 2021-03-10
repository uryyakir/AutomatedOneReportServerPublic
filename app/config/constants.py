import json
import configparser
import os
from pathlib import Path
# script will be run from /app directory


class ElasticsearchConstants:
    STATUS_INDEX_NAME = "users-report-data"

    COOKIES_INDEX_NAME = "users-report-cookies"

    TOKEN_INDEX_NAME = "users-tokens"

    SETTINGS_INDEX_NAME = "users-settings"

    IAP_BUYERS_INDEX_NAME = "users-iap-buyers"

    ELASTICSEARCH_URL = "https://search-automated-one-report-zh4avxnipujmsg5utqncknqaby.us-east-2.es.amazonaws.com"


class OnePratAPIConstants:
    URL = "https://one.prat.idf.il/api/Attendance/InsertPersonalReport"

    REQUEST_HEADERS = """{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "eu-US,en;q=0.5",
        "Access-Control-Allow-Origin": "*",
        "crossdomain": "true",
        "pragma": "no-cache",
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip,deflate,br"
    }"""

    SCHEDULED_SUBMISSION_HOUR = 11

    DEFAULT_SETTINGS = {
        "API_REPORT_TIME": "08:15"
    }

    POSSIBLE_REPORT_TIME = {
        "MINIMUM_POSSIBLE_REPORT_TIME": "05:15",
        "MAXIMUM_POSSIBLE_REPORT_TIME": "10:45"
    }

    with open('config/code_map.json', encoding='utf-8') as code_map_file:
        CODE_MAP = json.load(code_map_file)

    with open('config/outside_unit_options.json', encoding='utf-8') as outside_unit_options_file:
        OUTSIDE_UNIT_OPTIONS = json.load(outside_unit_options_file)


class AppVersion:
    LATEST_VERSION = "1.0"
    BREAKING_CHANGES = False
    SHOULD_NOTIFY = False


class Logs:
    FMT = "[%(levelname)s] %(asctime)s in %(filename)s (line %(lineno)d): %(message)s"
    DATE_FMT = '%d/%m/%Y %H:%M:%S'


class APN:
    base_path = Path(os.getcwd()).parent
    config = configparser.ConfigParser()
    config.read(f"{base_path}/creds/passwords.ini", encoding='utf8')
    KEY_ID = config["APN"]["key_id"]
    TEAM_ID = config["APN"]["team_id"]
    ALGORITHM = 'ES256'
    with open(f"{base_path}/creds/AuthKey_2MLY9HZ3R9.p8") as apns_auth_file:
        APNS_AUTH_KEY = apns_auth_file.read()

    TOKEN = None
    IAT = None
    BUNDLE_ID = 'club.automated-one-report'

    REPORT_SUCCESS_STATUS = {
        "True": ('הדיווח הושלם', 'דו"ח אחד נשלח בהצלחה!'),
        "False": ('הדיווח נכשל', 'דו"ח אחד לא נשלח כראוי!')
    }

    FILL_REPORT_REMINDER_STATUS = ("תזכורת להזנת דו\"ח 1!", "שמנו לב שלא הזנת את הסטטוס שלך לשבוע הבא, היכנס עכשיו :)")
