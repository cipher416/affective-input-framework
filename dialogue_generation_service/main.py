import pika
import speech_recognition as sr
import openai
import json
from transformers import pipeline, set_seed

import os
from dotenv import load_dotenv

load_dotenv('./dialogue_generation_service/.env')
print(os.getenv('OPENAI_API_KEY'))
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'analysis.emo'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)
openai.api_key = os.getenv('OPENAI_API_KEY')

def callback(ch, method, properties, body):
    body = json.loads(body.decode('UTF-8'))
    response = openai.Completion.create(
        model='gpt-3.5-turbo-instruct',
        prompt='Generate a response to the following text : ' + body['message'] + ' with the following emotion : ' + body['label']  
    )
    print(response)
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()

