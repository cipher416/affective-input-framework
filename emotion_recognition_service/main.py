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

def callback(ch, method, properties, body):
    body = json.loads(body.decode('UTF-8'))
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = properties.correlation_id),body=body['face'])

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('service started')
channel.start_consuming()

