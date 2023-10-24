import numpy as np
import pika
import base64
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import cv2
from keras.models import load_model

emotion_dict = {0: "angry", 1: "disgust", 2: "fear", 3: "happy", 4: "neutral", 5: "sad", 6: "surprise"}
face_classification_model = load_model("./facial_emotion_recognition_service/fer_model.h5")

face_detector = cv2.CascadeClassifier('./facial_emotion_recognition_service/haarcascades/haarcascade_frontalface_default.xml')


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'input.video'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)


    
def callback(ch, method, properties, body):
    with open('video.mp4', 'wb') as file:
        file.write(base64.b64decode(body))
    cap = cv2.VideoCapture('video.mp4')
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (1000, 600))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        total_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in total_faces:
            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
            crop_image = gray_frame[y:y + h, x:x + w]
            resized_image = np.expand_dims(np.expand_dims(cv2.resize(crop_image, (48, 48)), -1), 0)
            resized_image = resized_image / 255.0
            emotion_prediction = face_classification_model.predict(resized_image)
            frame = cv2.resize(frame, (1000, 600))
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            total_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
            index = int(np.argmax(emotion_prediction))
            channel.basic_publish(exchange='test', routing_key='emo.face', body=emotion_dict[index])

    

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('service started')
channel.start_consuming()
