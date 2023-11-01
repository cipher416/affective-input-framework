from fastapi import FastAPI, UploadFile, File
import uvicorn
import pika
import moviepy.editor as editor
import base64
import wave
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    
def callback(ch, method, properties, body):
    print(body)
    channel.stop_consuming()

@app.post("/")
async def root(file: bytes = File(...)):
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
    channel.basic_publish(exchange='test', routing_key='input.voice', body=base64.b64encode(wf))
    channel.basic_publish(exchange='test', routing_key='input.video', body=base64.b64encode(video_bytes))
    channel.start_consuming()
    return {"message": "Hello World"}

if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='test', exchange_type='topic')
    result = channel.queue_declare('')
    channel.exchange_declare(exchange='test', exchange_type='topic')
    queue_name = result.method.queue
    channel.queue_bind(
            exchange='test', queue=queue_name, routing_key='analysis.dialogue')
    channel.basic_consume(queue='', on_message_callback=callback,auto_ack=True)
    uvicorn.run(app, host='localhost', port=8000)
# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "output.wav"

# p = pyaudio.PyAudio()

# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 frames_per_buffer=CHUNK)

# print("* recording")

# frames = []

# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)

# print("* done recording")

# stream.stop_stream()
# stream.close()
# p.terminate()

# voice_binary_data = b''.join(frames)

# wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(voice_binary_data)
# wf.close()

# wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
# wf = wf.readframes(wf.getnframes())

# video = open('video.mp4', 'rb')
# video_bytes = video.read()



# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()

# channel.exchange_declare(exchange='test', exchange_type='topic')

# channel.basic_publish(exchange='test', routing_key='input.voice', body=base64.b64encode(wf))

# channel.basic_publish(exchange='test', routing_key='input.video', body=base64.b64encode(video_bytes))

# channel.basic_publish(exchange='test', routing_key='voice.text', body="test")

