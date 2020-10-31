from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import elasticsearch
from time import sleep
import datetime as dt


INDEX_NAME = "users-report-data"


class UserDataElasticHandler:
    def __init__(self, index_name: str):
        self.es = elasticsearch.Elasticsearch("https://search-automated-one-report-zh4avxnipujmsg5utqncknqaby.us-east-2.es.amazonaws.com")
        self.index_name = index_name

    def index_user_data(self, data_json):
        self.es.index(index=self.index_name, body=data_json)


class UserData(BaseModel):
    VENDOR_UUID: str
    DATE: str
    CODE: str
    TEXT: str
    SECONDARY_CODE: str
    SECONDARY_TEXT: str


elastic_handler = UserDataElasticHandler(index_name=INDEX_NAME)

class UserDataAPIHandler:
    """
    user data JSONs will look like that:
    {
        "VENDOR_UUID": "...",
        "DATE": 01/01/2020,
        "CODE": "...",
        "TEXT": "...",
        "SECONDARY_CODE": "...",
        "SECONDARY_TEXT": "..."
    }
    """
    app = FastAPI()

    @staticmethod
    @app.post("/index-user-data")
    async def index_user_data(request: UserData):
        print(request)
        await elastic_handler.index_user_data(request.json())
        return {"Hello": "World"}

    @staticmethod
    @app.get("/index-user-data")
    def index_user_data():
        return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("user-data-api-endpoint:UserDataAPIHandler.app", host='0.0.0.0', port=80, reload=True)
