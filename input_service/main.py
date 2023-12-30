from fastapi import FastAPI, UploadFile, File
import uvicorn
import pika
import json
import moviepy.editor as editor
import base64
import wave
from service_client import ServiceClient 
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv
from pydantic import BaseModel
dotenv.load_dotenv()

app = FastAPI()

class Chat(BaseModel):
    message: str

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_video_file(file: bytes):
    with open('file.webm', 'wb') as writeFile:
        writeFile.write(file)
        writeFile.close()
    video = editor.VideoFileClip(filename='file.webm')
    video.write_videofile('video.mp4')
    video.audio.write_audiofile('audio.wav')
    wf = wave.open('audio.wav', 'rb')
    wf = wf.readframes(wf.getnframes())
    video.close()
    video = open('video.mp4', 'rb')
    video_bytes = video.read()
    return wf, video_bytes

def call_services(audio_bytes, video_bytes):
    facial_emotion_client = ServiceClient(binding_key='input.video')
    facial_emotion_response = facial_emotion_client.call(base64.b64encode(video_bytes))
    speech_to_text_client = ServiceClient(binding_key='input.voice')
    speech_to_text_response = speech_to_text_client.call(base64.b64encode(audio_bytes))
    voice_tone_emotion_client= ServiceClient(binding_key='input.voice.tone')
    voice_tone_emotion_response = voice_tone_emotion_client.call(base64.b64encode(audio_bytes))
    text_emotion_recognition_service = ServiceClient(binding_key='voice.text')
    text_emotion_recognition_response = text_emotion_recognition_service.call(speech_to_text_response)
    emotion_recognition_service = ServiceClient(binding_key='analysis.emo')
    dialogue_generation_service = ServiceClient(binding_key='analysis.dialogue')
    emotion_recognition_response =  emotion_recognition_service.call(json.dumps({
        "voice":voice_tone_emotion_response.decode("utf-8") ,
        "text":text_emotion_recognition_response.decode("utf-8") ,
        "face":facial_emotion_response.decode("utf-8")
    }))
    print(speech_to_text_response)
    dialogue_generation_response = dialogue_generation_service.call(json.dumps({"message": speech_to_text_response.decode("utf-8") , "label": emotion_recognition_response.decode("utf-8")}))
    dialogue_generation_response = json.loads(dialogue_generation_response.decode("utf-8"))
    dialogue_generation_response['speech_transcript'] = speech_to_text_response.decode("utf-8")
    return dialogue_generation_response

def call_services_text(chat: Chat):
    text_emotion_recognition_service = ServiceClient(binding_key='voice.text')
    text_emotion_recognition_response = text_emotion_recognition_service.call(chat.message)
    print(text_emotion_recognition_response)
    dialogue_generation_service = ServiceClient(binding_key='analysis.dialogue')
    dialogue_generation_response = dialogue_generation_service.call(json.dumps({"message": chat.message , "label": text_emotion_recognition_response.decode('UTF-8')}))
    dialogue_generation_response = json.loads(dialogue_generation_response.decode("utf-8"))
    print(dialogue_generation_response)    
    dialogue_generation_response['speech_transcript'] = chat.message
    return dialogue_generation_response

@app.post("/")
async def root(file: bytes = File(...)):
    audio_bytes, video_bytes = read_video_file(file)
    response = call_services(audio_bytes, video_bytes)
    return response

@app.post("/text")
async def text(chat: Chat):
    print(chat)
    response = call_services_text(chat=chat)
    return response



if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    uvicorn.run(app, host=os.getenv("BACKEND_HOSTNAME"), port=8000)
