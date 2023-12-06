import pika
import speech_recognition as sr
from transformers import pipeline
import json
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv('./dialogue_generation_service/.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
emotion_dict = ["anger", "disgust",  "fear", "joy", "neutral",  "sadness",  "surprise"]

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
emo_text_binding_key = 'voice.text'
emo_ = ''
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=emo_text_binding_key)


def callback(ch, method, properties, body):
    body = body.decode('UTF-8')
    response = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages = [
            {"role": "system", "content": 'Translate the following text to english : ' + body}
        ]
    )
    translated_text = response.choices[0].message.content
    result = classifier(translated_text)[0]
    print(translated_text)
    filtered_result = [emo for emo in result if emo['label'] in emotion_dict]
    # channel.basic_publish(exchange='test', routing_key='emo.text', body=json.dumps({"message": body, "label": filtered_result[0]['label']}))
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = \
                                    properties.correlation_id),body=json.dumps({"message": body, "label": filtered_result[0]['label']}))
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("started")
channel.start_consuming()

