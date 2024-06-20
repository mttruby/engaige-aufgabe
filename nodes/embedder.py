from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Dict

class Embedder:
    
    def __init__(self, model: str = 'dbmdz/bert-base-german-cased'):

        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model)


    def embed_docs(self, documents: List[Dict]):
        
        n = len(documents)
        i = 1
        for doc in documents:
            inputs = self.tokenizer(doc['text'], return_tensors='pt', truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
            doc['embedding'] = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            print(f"Embedding document {i} of {n}")
            i += 1


    def get_embedding(self, text):
        
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    