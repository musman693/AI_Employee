from openai import AuthenticationError, OpenAI, OpenAIError
import os
import json
from fastapi import UploadFile
from fastapi import HTTPException
from app.config import settings

async def transcribe_and_analyze_audio(file: UploadFile):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    file_content = await file.read()
    temp_filename = f"temp_{file.filename}"
    
    with open(temp_filename, "wb") as f:
        f.write(file_content)

    try:
        with open(temp_filename, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        raw_text = transcript_response.text
    except AuthenticationError as exc:
        raise HTTPException(status_code=503, detail="OpenAI API key is missing or invalid. Update OPENAI_API_KEY in the backend .env file.") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI could not transcribe the meeting: {exc.message}") from exc
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    prompt = f"""
    Analyze the following meeting transcript and return JSON with keys:
    - summary: Concise summary of the meeting.
    - action_items: List of key action items and assignees.
    - speakers: List of identified speakers.
    - deadlines: List of deadlines mentioned.

    Transcript:
    "{raw_text}"
    """

    try:
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=503, detail="OpenAI API key is missing or invalid. Update OPENAI_API_KEY in the backend .env file.") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI could not summarize the meeting: {exc.message}") from exc

    result = json.loads(ai_response.choices[0].message.content or "{}")
    result["raw_transcript"] = raw_text
    return result
