import time
from fastapi import APIRouter, HTTPException
from src.utils.languageutils import text_to_audio

language = APIRouter()


@language.post('/text-audio', description="文字转语音")
async def text_audio(text: str, location: str):
    timestamp = str(time.time())
    file_path = 'static/audio/' + timestamp
    text_to_audio(text, file_path, location)
    return {"data": "static/audio/" + timestamp + ".wav"}

