import pika
import speech_recognition as sr
import base64

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
    audio_data = sr.AudioData(frame_data=base64.b64decode(body), sample_rate=RATE, sample_width=2, channels=1)
    result = recognizer.recognize_google(audio_data=audio_data, language='id', show_all=True)
    if len(result) == 0:
        result = 'nothing'
    else:
        result = result['alternative'][0]['transcript']
    # channel.basic_publish(exchange='test', routing_key='voice.text', body=result)
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = \
                                    properties.correlation_id),body=result)
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag='input')
print("started")
channel.start_consuming()

