from typing import Any


class WhisperService:
    async def transcribe(self, audio_bytes: bytes) -> str:
        return "Transcribed voice note"
