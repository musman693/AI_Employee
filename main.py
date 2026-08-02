from fastapi import FastAPI
from app.routers import meeting, document, legal
from app.routers import quotation, invoice, finance  # Module 3 — Shayan

app = FastAPI(
    title="AI Employee OS — Full Backend",
    description="Module 3 (Quotation/Invoice/Finance — Shayan) + Module 4 (Meeting/Document — Sultan)",
    version="1.0.0"
)

app.include_router(meeting.router, prefix="/api/v1/meeting", tags=["AI Meeting Assistant"])
app.include_router(document.router, prefix="/api/v1/document", tags=["AI Document Intelligence"])
app.include_router(legal.router, prefix="/api/v1/legal", tags=["AI Legal Assistant"])

# ── Module 3 — Shayan ────────────────────────────────────────────────────────
app.include_router(quotation.router, prefix="/api/v1/quotation", tags=["AI Quotation Generator"])
app.include_router(invoice.router,   prefix="/api/v1/invoice",   tags=["AI Invoice Generator"])
app.include_router(finance.router,   prefix="/api/v1/finance",   tags=["AI Finance Assistant"])

@app.get("/")
def root():
    return {
        "status": "online",
        "modules": {
            "module_3": "Quotation / Invoice / Finance (Shayan)",
            "module_4": "Meeting / Document Intelligence (Sultan)",
        },
    }