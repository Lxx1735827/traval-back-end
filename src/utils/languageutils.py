import websocket
import hashlib
import base64
import hmac
import json
import wave
from urllib.parse import urlencode
from fastapi import HTTPException
from wsgiref.handlers import format_date_time
import ssl
from datetime import datetime
from time import mktime
import _thread as thread
import os

# Mapping for different voice choices based on location/dialect
city_people = {
    "普通话": "xiaoyan",
    "四川话": "x2_xiaorong",
}

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, Text, wav_filename, people):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text
        self.wav_filename = wav_filename
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": people, "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        self.audio_chunks = []  # List to store audio chunks

    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: ws-api.xfyun.cn\n" + "date: " + date + "\n" + "GET /v2/tts HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode('utf-8')

        authorization_origin = f"api_key=\"{self.APIKey}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature_sha}\""
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }

        return url + '?' + urlencode(v)


def on_message(ws, message, wsParam):
    message = json.loads(message)
    code = message["code"]
    sid = message["sid"]
    audio = message["data"]["audio"]
    audio = base64.b64decode(audio)
    status = message["data"]["status"]

    if status == 2:
        wsParam.audio_chunks.append(audio)
        full_audio = b"".join(wsParam.audio_chunks)
        with open(wsParam.wav_filename+'.pcm', 'wb') as f:
            f.write(full_audio)
        pcm2wav(wsParam.wav_filename+'.pcm', wsParam.wav_filename+'.wav')
        os.remove(wsParam.wav_filename+'.pcm')
        ws.close()

    if code != 0:
        errMsg = message["message"]
        raise HTTPException(status_code=400, detail=errMsg)
    else:
        # Collect audio chunks
        wsParam.audio_chunks.append(audio)


def pcm2wav(pcm_file, wav_file, channels=1, bits=16, sample_rate=16000):
    print(pcm_file, wav_file)
    with open(pcm_file, 'rb') as pcmf:
        pcmdata = pcmf.read()

    if bits % 8 != 0:
        raise HTTPException(status_code=400, detail="bits % 8 must == 0. now bits:" + str(bits))

    with wave.open(wav_file, 'wb') as wavfile:
        wavfile.setnchannels(channels)
        wavfile.setsampwidth(bits // 8)
        wavfile.setframerate(sample_rate)
        wavfile.writeframes(pcmdata)


def on_open(ws, wsParam):
    def run(wsParam, *args):
        d = {"common": wsParam.CommonArgs, "business": wsParam.BusinessArgs, "data": wsParam.Data}
        ws.send(json.dumps(d))

    thread.start_new_thread(run, (wsParam,))


def text_to_audio(text, filename, location):
    wsParam = Ws_Param(APPID='223a24c2',
                       APISecret='ZjhlZDQyMDU3Y2NhYjMwYmExZGRmYmMy',
                       APIKey='e2f620fdc9d52be5e0f792d4e1755416',
                       Text=text,
                       wav_filename="src/"+filename,
                       people=city_people[location])

    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=lambda ws, msg: on_message(ws, msg, wsParam))
    ws.on_open = lambda ws: on_open(ws, wsParam)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    text_to_audio("你好，我们是不忘初心队，做的项目名称为云游名胜，欢迎使用", "output_audio", "安徽话")
