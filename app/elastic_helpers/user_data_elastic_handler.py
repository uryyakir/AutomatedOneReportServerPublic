from typing import Optional, Dict, Union, cast, List, Any
import datetime as dt
import elasticsearch  # type: ignore
# custom modules
from elastic_helpers import elastic_queries
from helpers import helpers
from config import constants


class UserDataElasticHandler:
    def __init__(self, index_name: str) -> None:
        self.es = elasticsearch.Elasticsearch(constants.ElasticsearchConstants.ELASTICSEARCH_URL)
        self.index_name = index_name

    def delete_old_status(self, vendor_uuid: str, curr_date: Optional[dt.date]) -> None:
        self.es.delete_by_query(index=self.index_name, body=elastic_queries.search_by_uuid(
            vendor_uuid=vendor_uuid,
            date_range_start=curr_date,
            date_range_end=curr_date)
        )

    def index_user_data(self, _type: str, data_json: Dict[str, Union[str, dt.datetime]]) -> None:
        """
        This function support indexing of status reports and cookies.
        In cases of status reports, there are two possible scenarios:
        1) All data fields are provided - that means the user has set some status. The function will delete old status (if one exists) and then index new status.
        2) Only VENDOR_UUID and DATE fields are provided - that means the user has set NO value for that date.
           If some status exists - we want to delete it (without indexing an alternative one).
        """
        if _type == "status":
            data_json["DATE"] = dt.datetime.strptime(cast(str, data_json["DATE"]), '%d/%m/%Y')
            # deletion is done for both use-cases
            self.delete_old_status(vendor_uuid=cast(str, data_json["VENDOR_UUID"]), curr_date=cast(dt.date, data_json["DATE"]))

            if all([data_json["MAIN_CODE"], data_json["TEXT"], data_json["SECONDARY_CODE"], data_json["SECONDARY_TEXT"]]):
                # first scenario
                self.es.index(index=self.index_name, body=data_json)

        elif _type in ("cookie", "settings", "token"):
            if _type == "cookie":
                data_json["COOKIE_EXPIRY_DATE"] = dt.datetime.strptime(cast(str, data_json["COOKIE_EXPIRY_DATE"]), '%d/%m/%Y')

            self.delete_old_status(vendor_uuid=cast(str, data_json["VENDOR_UUID"]), curr_date=None)
            self.es.index(index=self.index_name, body=data_json)

        else:  # _type == "iap_buyer"
            self.es.index(index=self.index_name, body=data_json)


    def get_user_data(self, _type: str, vendor_uuid: str) -> List[Dict[str, Any]]:
        date_range_start, date_range_end = helpers.get_relevant_days() if _type == "status" else (None, None)
        results = self.es.search(index=self.index_name, size=100, body=elastic_queries.search_by_uuid(
            vendor_uuid=vendor_uuid,
            date_range_start=date_range_start,
            date_range_end=date_range_end)
        )
        if _type == "settings" and results["hits"]["hits"]:
            return results["hits"]["hits"][0]["_source"]

        return results["hits"]["hits"]

    def get_all_today_data(self, _type: str, date_start: Optional[dt.date] = None, date_end: Optional[dt.date] = None, **kwargs) -> List[Dict[str, Any]]:
        total_results = []
        if _type == "status":
            if not date_start:
                curr_results = self.es.search(index=self.index_name, size=1000, scroll="3m", body=elastic_queries.search_by_date(date_start=dt.datetime.now().date(), date_end=dt.datetime.now().date()))

            elif date_start and date_end:
                curr_results = self.es.search(index=self.index_name, size=1000, scroll="3m", body=elastic_queries.search_by_date(date_start=date_start, date_end=date_end))

        elif _type == "settings":
            curr_results = self.es.search(index=self.index_name, size=1000, scroll="3m", body=elastic_queries.search_settings_by_hour(**kwargs))

        else:  # _type = "cookie" or _type = "token"
            curr_results = self.es.search(index=self.index_name, size=1000, scroll="3m", body=elastic_queries.search_all())

        while len(curr_results["hits"]["hits"]):
            scroll_id = curr_results["_scroll_id"]
            total_results += curr_results["hits"]["hits"]
            curr_results = self.es.scroll(scroll_id=scroll_id, scroll="3m")

        return total_results


class Handlers:
    elastic_handler = UserDataElasticHandler(index_name=constants.ElasticsearchConstants.STATUS_INDEX_NAME)
    cookies_handler = UserDataElasticHandler(index_name=constants.ElasticsearchConstants.COOKIES_INDEX_NAME)
    token_handler = UserDataElasticHandler(index_name=constants.ElasticsearchConstants.TOKEN_INDEX_NAME)
    settings_handler = UserDataElasticHandler(index_name=constants.ElasticsearchConstants.SETTINGS_INDEX_NAME)
    iap_buyers_handler = UserDataElasticHandler(index_name=constants.ElasticsearchConstants.IAP_BUYERS_INDEX_NAME)
