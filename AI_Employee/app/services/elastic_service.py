from elasticsearch import Elasticsearch
import pytesseract
from PIL import Image
import io
from app.config import settings

es = Elasticsearch(settings.ELASTICSEARCH_URL)
INDEX_NAME = "ai_documents"

def init_es_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "document_id": {"type": "keyword"},
                        "filename": {"type": "text"},
                        "content": {"type": "text"}
                    }
                }
            }
        )

async def extract_text_and_index(file_bytes: bytes, filename: str, doc_id: str):
    init_es_index()
    image = Image.open(io.BytesIO(file_bytes))
    extracted_text = pytesseract.image_to_string(image)

    document = {
        "document_id": doc_id,
        "filename": filename,
        "content": extracted_text
    }
    
    response = es.index(index=INDEX_NAME, id=doc_id, body=document)
    return extracted_text, response['result']

def search_documents(query: str):
    search_query = {"query": {"match": {"content": query}}}
    try:
        response = es.search(index=INDEX_NAME, body=search_query)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception:
        return []