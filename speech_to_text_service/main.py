import pika
import speech_recognition as sr
import base64
import wave
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv(dotenv_path='.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

CHUNK = 1024
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'input.voice'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)
recognizer = sr.Recognizer()

def callback(ch, method, properties, body):
    result = 'nothing'
    try:
        audio_file = open('audio.wav', "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language='id'
        )
        result = transcript.text
        print(result)
        # channel.basic_publish(exchange='test', routing_key='voice.text', body=result)
    finally:
        channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = \
                                        properties.correlation_id),body=result)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag='input')
print("started")
channel.start_consuming()

