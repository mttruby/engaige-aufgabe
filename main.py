from typing import List, Dict
from elastic_docstore import ESDocStore
from embedder import Embedder
from generator import AnswerGenerator
import pymupdf
import os


def files_to_docs(docs_dir: str, documents: List[Dict], chunk_size: int):

    for file in os.listdir(docs_dir):
        if not file.endswith('.pdf'): continue
    
    doc = pymupdf.open(os.path.join(docs_dir, file))
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text += page.get_text()

    words = full_text.split()
    
    # Teile in Abschnitte von chunk_size worten auf
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    for chunk in chunks:
        documents.append({'text': chunk})


def index_documents(doc_store: ESDocStore, docs_dir: str):
    
    docs = []
    files_to_docs(docs_dir=docs_dir, documents=docs, chunk_size=100)
    
    embedder.embed_docs(documents=docs[:5])
    
    doc_store.clear()
    doc_store.write_documents(documents=docs[:5])


def query(question: str, doc_store: ESDocStore, embedder: Embedder, generator: AnswerGenerator):
    
    embedding = embedder.get_embedding(question)
    search_result = doc_store.search(embedding)
    
    context = ""

    for hit in search_result['hits']['hits']:
       context += f"Kontext: {(hit['_source']['text'])} "

    answer = generator.generate_answer(question, context)
    return answer   
        
    

if __name__ == '__main__':

    embedder = Embedder("dbmdz/bert-base-german-cased")
    doc_store = ESDocStore(host='localhost', port=9200, index="entwicklertask")
    generator = AnswerGenerator("DiscoResearch/Llama3-DiscoLeo-Instruct-8B-v0.1")

    # index_documents(doc_store=doc_store, docs_dir="data")

    try:
       
        while True:
    
            question = input("Stelle Deine Frage: ")
            answer = query(question, doc_store=doc_store, embedder=embedder, generator=generator)
    
            print(f"\nAntwort: {answer}\n\n")
    
    except KeyboardInterrupt:
        print('Stopped.')
