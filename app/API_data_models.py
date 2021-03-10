from typing import Optional
from pydantic import BaseModel


class UserData(BaseModel):
    VENDOR_UUID: str
    DATE: str
    MAIN_CODE: Optional[str]
    TEXT: Optional[str]
    SECONDARY_CODE: Optional[str]
    SECONDARY_TEXT: Optional[str]


class UserCookie(BaseModel):
    VENDOR_UUID: str
    COOKIE_STRING: str
    COOKIE_EXPIRY_DATE: str


class UserUUID(BaseModel):
    VENDOR_UUID: str


class UserSettings(BaseModel):
    VENDOR_UUID: str
    API_REPORT_TIME: str


class IAPBuyer(BaseModel):
    VENDOR_UUID: str
    PRODUCT_ID: str


class TokenUUID(BaseModel):
    VENDOR_UUID: str
    TOKEN: str
