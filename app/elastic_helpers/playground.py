from typing import Dict, Any
import elasticsearch  # type: ignore
from pprint import pprint
from config import constants


class AutomatedOneReportElasticHandler:
    def __init__(self, index_name: str):
        self.es = elasticsearch.Elasticsearch(constants.ElasticsearchConstants.ELASTICSEARCH_URL)
        self.index_name = index_name

    def create_index(self) -> None:
        create_response = self.es.indices.create(index=self.index_name)
        print(create_response)

    def delete_index_data(self) -> None:
        resp = self.es.delete_by_query(index=self.index_name, body={
            "query": {
                "match_all": {}
            }
        })
        pprint(resp)

    def get_index_data(self) -> None:
        result = self.es.search(index=self.index_name, size=10, body={
            "query": {
                "match_all": {}
            }
        })
        pprint(result)

    def update_index_data(self, _id: str, body: Dict[str, Dict[str, Any]]):
        self.es.update(index=self.index_name, id=_id, doc_type="_doc", body=body)

    def get_mapping(self) -> None:
        mapping = self.es.indices.get_mapping(index=self.index_name)
        pprint(mapping)

    def clear_mapping(self) -> None:
        self.es.indices.delete(index=self.index_name)
        self.es.indices.refresh()
        self.create_index()


if __name__ == "__main__":
    # cookie_handler = AutomatedOneReportElasticHandler(constants.ElasticsearchConstants.COOKIES_INDEX_NAME)
    # status_handler = AutomatedOneReportElasticHandler(constants.ElasticsearchConstants.STATUS_INDEX_NAME)
    token_handler = AutomatedOneReportElasticHandler(constants.ElasticsearchConstants.TOKEN_INDEX_NAME)
    # handler.create_index()
    # handler.delete_index_data()
    token_handler.get_index_data()
    # handler.get_mapping()
