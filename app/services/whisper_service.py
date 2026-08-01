import openai
import os
import json
from fastapi import UploadFile
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

async def transcribe_and_analyze_audio(file: UploadFile):
    file_content = await file.read()
    temp_filename = f"temp_{file.filename}"
    
    with open(temp_filename, "wb") as f:
        f.write(file_content)

    try:
        with open(temp_filename, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe(
                model="whisper-1", 
                file=audio_file
            )
        raw_text = transcript_response.get("text", "")
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

    ai_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(ai_response.choices[0].message.content)
    result["raw_transcript"] = raw_text
    return result