import time
import os
from fastapi import APIRouter
from fastapi import File, UploadFile
from typing import Dict
from src.utils.languageutils import text_to_audio
from src.utils.languageutils2 import audio_to_text
from src.utils.aiutils import completion2

language = APIRouter()


@language.post('/text-audio', description="文字转语音")
async def text_audio(text: str, location: str):
    timestamp = str(time.time())
    file_path = 'static/audio/' + timestamp
    text_to_audio(text, file_path, location)
    return {"data": "static/audio/" + timestamp + ".wav"}


@language.post('/audio-text', description="语音转文字")
async def audio_text(file: UploadFile = File(...)) -> Dict[str, str]:
    file_suffix = file.filename.split('.')[-1]
    timestamp = str(time.time())
    file_location = "static/audio/" + timestamp + file_suffix
    with open(file_location, "wb") as buffer:
        file_content = await file.read()
        buffer.write(file_content)
    data = audio_to_text(file_location)
    os.remove(file_location)
    return {
        "data": data
    }


@language.post('/audio-audio', description="语音对话")
async def audio_audio(location: str, file: UploadFile = File(...)):
    # 语音转文字
    file_suffix = file.filename.split('.')[-1]
    timestamp = str(time.time())
    file_location = "static/audio/" + timestamp + file_suffix
    with open(file_location, "wb") as buffer:
        file_content = await file.read()
        buffer.write(file_content)
    data = audio_to_text(file_location)+"简单回复，不超过30字"
    os.remove(file_location)
    # AI对话
    result = completion2(data)
    timestamp = str(time.time())
    file_path = 'static/audio/' + timestamp
    text_to_audio(result, file_path, location)
    return {"data": "static/audio/" + timestamp + ".wav"}



