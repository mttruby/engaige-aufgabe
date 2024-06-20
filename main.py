from typing import List, Dict
from nodes.elastic_docstore import ESDocStore
from nodes.embedder import Embedder
from nodes.generator import AnswerGenerator
import pymupdf
import os
import yaml


def files_to_docs(docs_dir: str, documents: List[Dict], chunk_size: int):

    # Überspringen, was kein PDF ist
    for file in os.listdir(docs_dir):
        if not file.endswith('.pdf'): continue
    
    # Alles zusammenfassen, um dann in chunks von bestimtmen Wort-Anzahlen aufzuteilen
    # Schien mir sinnvoller, als ein chunk pro PDF-Seite
    doc = pymupdf.open(os.path.join(docs_dir, file))
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text += page.get_text()

    words = full_text.split()
    
    # Teile in Abschnitte von chunk_size Worten auf
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    for chunk in chunks:
        documents.append({'text': chunk})


def index_documents(doc_store: ESDocStore, docs_dir: str):
    
    # Text aus PDF-Dateien  extrahieren
    docs = []
    files_to_docs(docs_dir=docs_dir, documents=docs, chunk_size=100)
    
    # Embeddings generieren
    embedder.embed_docs(documents=docs)
    
    # DocumentStore löschen und neu beschreiben
    doc_store.clear()
    doc_store.write_documents(documents=docs)


def query(question: str, doc_store: ESDocStore, embedder: Embedder, generator: AnswerGenerator):
    

    # Retrieval
    embedding = embedder.get_embedding(question)
    search_result = doc_store.search(embedding)
    
    
    # Die relevanten Textpassagen zu einer kombinieren, um sie dem LLM
    # als Kontext zu geben.
    context = ""

    for hit in search_result['hits']['hits']:
       context += f"Kontext: {(hit['_source']['text'])} "


    # Antwort generieren   
    answer = generator.generate_answer(question, context)
    return answer        
    

if __name__ == '__main__':

    with open('credentials.yaml', 'r') as file:
        creds = yaml.safe_load(file)

    doc_store = ESDocStore(host='localhost', port=9200, index="entwicklertask",
                           username=creds['user'], password=creds['password'])

    embedder = Embedder("dbmdz/bert-base-german-cased")
    generator = AnswerGenerator("DiscoResearch/Llama3-DiscoLeo-Instruct-8B-v0.1")

    index_documents(doc_store=doc_store, docs_dir="data")

    try:
       
        while True:
    
            question = input("Stelle Deine Frage: ")
            answer = query(question, doc_store=doc_store, embedder=embedder, generator=generator)
    
            print(f"\n\nAntwort: {answer}\n\n")
    
    except KeyboardInterrupt:
        print('Stopped.')
