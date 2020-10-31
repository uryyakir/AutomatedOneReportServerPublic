import elasticsearch
from pprint import pprint


INDEX_NAME = "users-report-data"


class AutomatedOneReportElasticHandler:
    def __init__(self, index_name: str):
        self.es = elasticsearch.Elasticsearch("https://search-automated-one-report-zh4avxnipujmsg5utqncknqaby.us-east-2.es.amazonaws.com")
        self.index_name = index_name

    def create_index(self):
        create_response = self.es.indices.create(index=self.index_name)
        print(create_response)

    def delete_index_data(self):
        resp = self.es.delete_by_query(index=self.index_name, body={
            "query": {
                "match_all": {}
            }
        })
        pprint(resp)

    def get_index_data(self):
        result = self.es.search(index=self.index_name, size=10, body={
            "query": {
                "match_all": {}
            }
        })
        pprint(result)


if __name__ == "__main__":
    handler = AutomatedOneReportElasticHandler(INDEX_NAME)
    # handler.delete_index_data()
    handler.get_index_data()
