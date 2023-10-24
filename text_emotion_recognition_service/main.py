import pika
import speech_recognition as sr
from transformers import pipeline
from translate import Translator
import json
emotion_dict = ["anger", "disgust",  "fear", "joy",  "neutral",  "sadness",  "surprise"]

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
translator = Translator(to_lang='en')
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
    body = translator.translate(body.decode('UTF-8'))
    result = classifier(body)[0]
    print(result)
    filtered_result = [emo for emo in result if emo['label'] in emotion_dict]
    channel.basic_publish(exchange='test', routing_key='emo.text', body=json.dumps({"message": body, "label": filtered_result[0]['label']}))
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("started")
channel.start_consuming()
