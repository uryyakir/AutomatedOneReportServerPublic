from typing import Dict, Any, cast
import datetime as dt


def search_all() -> Dict[str, Any]:
    return {
        "query": {
            "match_all": {}
        }
    }


def search_by_date(date_start: dt.date, date_end: dt.date) -> Dict[str, Any]:
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "DATE": {
                                "gte": date_start.strftime("%d/%m/%Y"),
                                "lte": date_end.strftime("%d/%m/%Y"),
                                "format": "dd/MM/yyyy"
                            }
                        }
                    }
                ]
            }
        }
    }


def search_by_uuid(vendor_uuid: str, date_range_start: dt.date = None, date_range_end: dt.date = None) -> Dict[str, Any]:
    if all([date_range_start, date_range_end]):
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"VENDOR_UUID.keyword": vendor_uuid}
                        },
                        {
                            "range": {
                                "DATE": {
                                    "gte": cast(dt.date, date_range_start).strftime("%d/%m/%Y"),
                                    "lte": cast(dt.date, date_range_end).strftime("%d/%m/%Y"),
                                    "format": "dd/MM/yyyy"
                                }
                            }
                        }
                    ]
                }
            }
        }
    else:  # query is strictly using vendor_uuid
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"VENDOR_UUID.keyword": vendor_uuid}
                        }
                    ]
                }
            }
        }
    return search_query


def search_settings_by_hour(hour: str) -> Dict[str, Any]:
    return {
        "query": {
            "match": {"API_REPORT_TIME.keyword": hour}
        }
    }
