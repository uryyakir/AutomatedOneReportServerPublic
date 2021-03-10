import json
import jwt
import time
from config import constants
from hyper import HTTPConnection


class JWTToken:
    @staticmethod
    def create_token() -> None:
        constants.APN.IAT = time.time()
        constants.APN.TOKEN = jwt.encode(
            {
                'iss': constants.APN.TEAM_ID,
                'iat': constants.APN.IAT
            },
            constants.APN.APNS_AUTH_KEY,
            algorithm=constants.APN.ALGORITHM,
            headers={
                'alg': constants.APN.ALGORITHM,
                'kid': constants.APN.KEY_ID,
            }
        )

    @staticmethod
    def check_iat() -> None:
        curr_time = time.time()
        if not constants.APN.IAT:
            JWTToken.create_token()

        elif curr_time - constants.APN.IAT > 20 * 60:  # 20 minutes since creating JWT token
            JWTToken.create_token()

    @staticmethod
    def get_token() -> bytes:
        JWTToken.check_iat()
        return constants.APN.TOKEN


def send_report_success_status(registration_id: str, success: bool) -> None:
    title, body = constants.APN.REPORT_SUCCESS_STATUS[str(success)]
    send_push(registration_id, title, body)


def send_push(registration_id: str, title: str, body: str) -> None:
    path = '/3/device/{0}'.format(registration_id)
    request_headers = {
        'apns-expiration': '0',
        'apns-priority': '10',
        'apns-topic': constants.APN.BUNDLE_ID,
        'apns-push-type': 'alert',
        'authorization': 'bearer {0}'.format(JWTToken.get_token().decode('ascii'))
    }

    payload_data = {
        'aps': {
            'alert': {
                'title': title,
                'body': body
            },
            "sound": "default"
        }
    }
    payload = json.dumps(payload_data).encode('utf-8')

    conn = HTTPConnection('api.push.apple.com:443')
    conn.request(
        'POST',
        path,
        payload,
        headers=request_headers
    )
    _ = conn.get_response()
