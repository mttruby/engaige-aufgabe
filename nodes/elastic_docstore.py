from elasticsearch import Elasticsearch
from typing import List, Dict


class ESDocStore:
    
    def __init__(self, host: str, port: int, index: str, password: str, username: str = "elastic", cert_path: str = "http_ca.crt"):

        self.index = index
        self.client = Elasticsearch(
            f"https://{host}:{port}",
            ca_certs=cert_path,
            basic_auth=(username, password))

        if self.client.ping() == False:
            raise ValueError("Connection to Elasticsearch failed.")
        else:
            print("Connected to Elasticsearch.")


    def clear(self):
        self.client.options(ignore_status=[400,404]).indices.delete(index=self.index)


    def write_documents(self, documents: List[Dict]):

        if self.client.indices.exists(index=self.index) == False:
                self.client.indices.create(index=self.index)

        for i, doc in enumerate(documents):
            self.client.index(index=self.index, id=i, document=doc)


    def search(self, query_embedding):
        response = self.client.search(
        index=self.index,
        body={
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": 5,
                "num_candidates": 100
            },
            "_source": ["text"]
        })
        return response
