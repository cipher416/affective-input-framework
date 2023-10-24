import pika
import speech_recognition as sr
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
consumed_binding_keys = []
binding_keys = ['emo.text', 'emo.face', 'emo.voice']
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
message = ''
emotions = []
channel.queue_bind(
            exchange='test', queue=queue_name, routing_key='emo.*')

def callback(ch, method, properties, body):
    global message
    print(consumed_binding_keys, method.routing_key)
    if method.routing_key == 'emo.text':
        try:
            message = json.loads(body.decode('UTF-8'))['message']
            print(message)
            emotions.append(body.decode('UTF-8'))
        except:
            consumed_binding_keys.clear()
            return
    if len(consumed_binding_keys) < len(binding_keys):
        consumed_binding_keys.append(method.routing_key)
        emotions.append(body.decode('UTF-8'))
        if len(consumed_binding_keys) == len(binding_keys):
            consumed_binding_keys.clear()
            print('sending to dialogue service')
            print(message)
            channel.basic_publish(exchange='test', routing_key='analysis.emo', body=json.dumps({"message": message, "label": emotions[0]}))
            emotions.clear()
            message = ''


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('service started')
channel.start_consuming()

