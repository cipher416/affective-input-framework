import pika
import speech_recognition as sr
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
            exchange='test', queue=queue_name, routing_key='analysis.emo')
weights_mapping = {
    "voice": 0.3,
    "text": 0.5,
    "face": 0.2
}

def choose_emotion(emotions_dict):
    emotion_weights = {"neutral": 0}
    print(emotions_dict)
    for key, val in emotions_dict.items():
        if val in emotion_weights:
            emotion_weights[val] += weights_mapping[key]
        else:
            emotion_weights[val] = weights_mapping[key]
    sorted(emotion_weights.keys(), key=lambda x:x[1])
    print(emotion_weights)
    return list(emotion_weights.keys())[0]
    

def callback(ch, method, properties, body):
    body = json.loads(body.decode('UTF-8'))
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = properties.correlation_id),body=choose_emotion(body))

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('service started')
channel.start_consuming()

