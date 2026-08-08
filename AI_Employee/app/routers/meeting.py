from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.s3_service import upload_file_to_s3
from app.services.whisper_service import transcribe_and_analyze_audio

router = APIRouter()

@router.post("/process-meeting")
async def process_meeting(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp3', '.wav', '.m4a', '.mp4')):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    file_url = await upload_file_to_s3(file, folder="meetings")
    await file.seek(0)
    analysis = await transcribe_and_analyze_audio(file)
    analysis["file_url"] = file_url
    
    return {"status": "success", "data": analysis}
