import pyaudio
import wave
import pika
import base64

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

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

wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
wf = wf.readframes(wf.getnframes())

video = open('video.mp4', 'rb')
video_bytes = video.read()



connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='test', exchange_type='topic')

channel.basic_publish(exchange='test', routing_key='input.voice', body=base64.b64encode(wf))

channel.basic_publish(exchange='test', routing_key='input.video', body=base64.b64encode(video_bytes))

# channel.basic_publish(exchange='test', routing_key='voice.text', body="test")