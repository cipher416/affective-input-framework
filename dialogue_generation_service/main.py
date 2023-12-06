import pika
import speech_recognition as sr
from openai import OpenAI
import json
from transformers import pipeline, set_seed

import os
from dotenv import load_dotenv
load_dotenv('./dialogue_generation_service/.env')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'analysis.dialogue'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)

def callback(ch, method, properties, body):
    body = json.loads(body.decode('UTF-8'))
    print(body)
    response = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages=[
            {"role": "system","content": 'You are a conversational agent. Generate a response to the following text : ' + body['message'] + ' with the following emotion : ' + body['label'] + '. The response must be in the Indonesian language.'}
        ]
    )
    print(response)
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = \
                                    properties.correlation_id),body=json.dumps({"message":response.choices[0].message.content,"emotion":body['label']}))
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()

