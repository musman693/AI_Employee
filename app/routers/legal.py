from fastapi import APIRouter
from pydantic import BaseModel
import openai
import json
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY
router = APIRouter()

class ContractAnalysisRequest(BaseModel):
    contract_text: str

@router.post("/analyze-contract")
async def analyze_contract(payload: ContractAnalysisRequest):
    prompt = f"""
    You are an AI Legal Assistant. Analyze the contract text and return JSON:
    - risk_level: High/Medium/Low
    - risky_clauses: List of problematic clauses
    - summary: Executive legal summary

    Contract:
    "{payload.contract_text}"
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    analysis = json.loads(response.choices[0].message.content)
    return {"status": "success", "analysis": analysis}