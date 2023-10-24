import wave
import librosa
import numpy as np
import pika
import base64
import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from keras.models import Sequential
from keras.models import load_model

CHUNK = 1024
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

def extract_features(data):
    result = np.array([])
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
    result=np.hstack((result, zcr)) 

    stft = np.abs(librosa.stft(data))
    chroma_stft = np.mean(librosa.feature.chroma_stft(S=stft, sr=RATE).T, axis=0)
    result = np.hstack((result, chroma_stft)) 

    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=RATE).T, axis=0)
    result = np.hstack((result, mfcc)) 

    rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
    result = np.hstack((result, rms))

    mel = np.mean(librosa.feature.melspectrogram(y=data, sr=RATE).T, axis=0)
    result = np.hstack((result, mel)) 
    
    return result

def get_features(path):
    data, _ = librosa.load(path, duration=2.5, offset=0.6)
    res1 = extract_features(data)
    result = np.array(res1)
    return result

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'input.voice'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)

# pickle_ser_file = open('speech_emotion_model.pickle', 'rb')
# model = pickle.load(pickle_ser_file)
# pickle_ser_file.close()
model = load_model('./emotional_speech_recognition_service/speech_emotion_model.h5')
pickle_encoder = open('./emotional_speech_recognition_service/speech_emotion_encoder.pickle', 'rb')
encoder = pickle.load(pickle_encoder)
pickle_encoder.close()
    
def callback(ch, method, properties, body):
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(data=base64.b64decode(body))
    wf.close()
    features = get_features(WAVE_OUTPUT_FILENAME)
    a = []
    a.append(features)
    features = pd.DataFrame(a)
    scaler = StandardScaler()
    x_test = scaler.fit_transform(features.iloc[: ,])
    x_test = np.expand_dims(x_test, axis=2)
    result = model.predict(x_test)
    result = np.array(result)
    transformed_result = encoder.inverse_transform(result)
    channel.basic_publish(exchange='test', routing_key='emo.voice', body=transformed_result[0][0])
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()

