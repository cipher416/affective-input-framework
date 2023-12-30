import pika
import speech_recognition as sr
import json
from transformers import pipeline, set_seed
import os
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

client = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = ''
binding_key = 'analysis.dialogue'
channel.exchange_declare(exchange='test', exchange_type='topic')
result = channel.queue_declare('')
queue_name = result.method.queue
channel.queue_bind(
        exchange='test', queue=queue_name, routing_key=binding_key)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,input_key="message")
def callback(ch, method, properties, body):
    body = json.loads(body.decode('UTF-8'))
    print(body)
    # response = client.chat.completions.create(
    #     model='gpt-3.5-turbo-1106',
    #     messages=[
    #         {"role": "system","content": 'You are a conversational agent. Generate a response to the following text : ' + body['message'] + ' with the following emotion : ' + body['label'] + '. The response must be in the Indonesian language.'}
    #     ]
    # )
    template = """
    You are a conversational agent. Generate a response to the user with the following emotion : {emotion}. 
    The response must be in the Indonesian language, and only contain the assistant's response.
    """
    prompt = ChatPromptTemplate.from_messages(
        messages=[
            SystemMessagePromptTemplate.from_template(
                template=template
            ),
            MessagesPlaceholder(
                variable_name='chat_history'
            ),
            HumanMessagePromptTemplate.from_template(
                "{message}"
            )
        ]
    )
    llm_chain = LLMChain(prompt=prompt,llm=client,memory=memory,verbose=True)
    response = llm_chain.predict(message=body['message'],emotion=body['label'])
    channel.basic_publish(exchange='test', routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id = \
                                    properties.correlation_id),body=json.dumps({"message":response,"emotion":body['label']}))
    return

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()

