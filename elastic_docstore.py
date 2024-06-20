from elasticsearch import Elasticsearch
from transformers import BertModel, BertTokenizer
import torch
from embedder import Embedder
from typing import List, Dict
from os import getenv


class ESDocStore:
    
    def __init__(self, host: str, port: int, index: str):

        self.index = index
        self.client = Elasticsearch(
            f"https://{host}:{port}",
            ca_certs="http_ca.crt",
            basic_auth=(getenv("ELASTIC_USER", "elastic"), getenv("ELASTIC_PASSWORD", "iAYFSCBwZX9Ps=9IZmh4")))

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
