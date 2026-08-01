from fastapi import FastAPI
from app.routers import meeting, document, legal

app = FastAPI(
    title="AI Employee OS - Meeting & Document Intelligence API",
    version="1.0.0"
)

app.include_router(meeting.router, prefix="/api/v1/meeting", tags=["AI Meeting Assistant"])
app.include_router(document.router, prefix="/api/v1/document", tags=["AI Document Intelligence"])
app.include_router(legal.router, prefix="/api/v1/legal", tags=["AI Legal Assistant"])

@app.get("/")
def root():
    return {"status": "online", "message": "Module 4 Backend Services Running"}