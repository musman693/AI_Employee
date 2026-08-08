from fastapi import APIRouter, UploadFile, File
import uuid
from app.services.s3_service import upload_file_to_s3
from app.services.elastic_service import extract_text_and_index, search_documents

router = APIRouter()

@router.post("/upload-ocr")
async def upload_and_process_document(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    file_bytes = await file.read()
    await file.seek(0)
    s3_url = await upload_file_to_s3(file, folder="documents")
    extracted_text, index_status = await extract_text_and_index(file_bytes, file.filename, doc_id)
    
    return {
        "document_id": doc_id,
        "s3_url": s3_url,
        "indexing_status": index_status,
        "extracted_snippet": extracted_text[:200]
    }

@router.get("/search")
async def search_docs(q: str):
    results = search_documents(q)
    return {"query": q, "results": results}
