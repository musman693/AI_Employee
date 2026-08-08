from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AuthenticationError, OpenAI, OpenAIError
import json
from app.config import settings

router = APIRouter()

class ContractAnalysisRequest(BaseModel):
    contract_text: str

@router.post("/analyze-contract")
async def analyze_contract(payload: ContractAnalysisRequest):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
    You are an AI Legal Assistant. Analyze the contract text and return JSON:
    - risk_level: High/Medium/Low
    - risky_clauses: List of problematic clauses
    - summary: Executive legal summary

    Contract:
    "{payload.contract_text}"
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=503, detail="OpenAI API key is missing or invalid. Update OPENAI_API_KEY in the backend .env file.") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI could not analyze the contract: {exc.message}") from exc
    
    analysis = json.loads(response.choices[0].message.content or "{}")
    return {"status": "success", "analysis": analysis}
