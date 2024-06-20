from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os, json
import certifi
import random
from pymongo import MongoClient
from flask_pymongo import PyMongo
from langchain.schema import messages_from_dict, messages_to_dict

import langchain_openai as lcai
from utils import mLangChain
from agents import *

from langchain_community.document_loaders import WebBaseLoader
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from sentiment import analyze_sentiment

from dotenv import load_dotenv
from uuid import uuid4
import datetime
import redis
from flask_session import Session
load_dotenv("project.env")

DB_NAME = "test"

print(os.getenv("AZURE_OPENAI_ENDPOINT"))

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key1'  # Required for session to work
# app.config["MONGO_URI"] = os.getenv("AZURE_COSMOS_MONGO_CONNSTRING")
# mongo = PyMongo(app, tlsCAFile=certifi.where())
# client = mongo.cx
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

Session(app)

# db = client[DB_NAME]
# print(client.list_databases())
client = MongoClient('localhost', 27017)

db = client.flask_db
chat_history_collection = db.chat_history_collection
chat_client_info = db.chat_client_info
chat_emo_feedback = db.chat_emo_feedback

sender_agent = None
chat_history = [
]
initQueue = [
    { "id": 1, "name": "Lucy", "product": "Airline" , "grateful": 0, "ranting": 0, "expression":0, "civil": 0, "info": 1, "emo": 1},
    { "id": 2, "name": "Esther", "product": "Hotel", "grateful": 1, "ranting": 0, "expression": 1, "civil": 1, "info": 1, "emo": 0},
    { "id": 3, "name": "Peter", "product": "Airline",  "grateful": 1, "ranting": 1, "expression": 1, "civil": 1, "info": 0, "emo": 1},
    { "id": 4, "name": "Joseph", "product": "Hotel" , "grateful": 0, "ranting": 1, "expression":0, "civil": 0, "info": 0, "emo": 0}
]
clientQueue = initQueue.copy()

TYPE_EMO_THOUGHT = "You might be thinking"
TYPE_EMO_SHOES = "Put Yourself in the Client's Shoes"
TYPE_EMO_REFRAME = "Be Mindful of Your Emotions"
TYPE_SENTIMENT = "Client's Sentiment"


sender_initial = agent_sender_fewshot_twitter()
sender_agent = mAgentCustomer()
# perspective / thoughts

# reframing
emo_agent = mAgentER()
# shoes
ep_agent = mAgentEP()
info_agent = mAgentInfo()
trouble_agent = mAgentTrouble()


@app.route('/')
def hello():
    return render_template('landing.html')

 # just for testing
@app.route('/chat')
def start_chat(): 
    return render_template('feedback.html')

# @app.route('/chat')
# def start_chat(): 
#     global clientQueue
#     if not clientQueue:
#         clientQueue = initQueue
#     random.shuffle(clientQueue)
#     client = clientQueue.pop(0)
#     session_id = str(uuid4())   ### unique to each user/participant/representative
#     # 
#     current_client = client['name']
#     session[session_id] = {}
#     session[session_id]['current_client'] = current_client
#     clientParam = f"?product={client['product']}&grateful={client['grateful']}&ranting={client['ranting']}&expression={client['expression']}&civil={client['civil']}&info={client['info']}&emo={client['emo']}"
  
#     return redirect(url_for('index', session_id=session_id) + clientParam)


@app.route('/<session_id>/')
def index(session_id):
    if session_id in session:
        current_client = session[session_id]['current_client']
    else:
        current_client = 'Guest'

    return render_template('index_chat.html', session_id=session_id, current_client=current_client)



@app.route('/<session_id>/get-reply', methods=['GET','POST'])
def getReply(session_id):
    global clientQueue
    if request.method == 'GET':
        val_product = request.args.get('product')
        val_grateful = request.args.get('grateful')
        val_ranting = request.args.get('ranting')
        val_expression = request.args.get('expression')
        val_civil = request.args.get('civil')
        show_info = request.args.get('info')
        show_emo = request.args.get('emo')

        complaint_parameters = {
            "product": val_product,
            "is_grateful": 'grateful' if val_grateful==0 else 'NOT grateful',
            "is_ranting": 'ranting' if val_ranting==0 else 'NOT ranting',
            "is_expression": 'expression' if val_expression==0 else 'NOT expression'
        }

        response = sender_initial.invoke(complaint_parameters)

        client_id = str(uuid4())
        current_client = session[session_id]['current_client']
        session[session_id][client_id] = {"current_client": current_client, "product": val_product, "civil": val_civil, "chat_history": []}
        session[session_id][client_id]["chat_history"] = messages_to_dict([AIMessage(content=response)])
        

        turn_number = len(session[session_id][client_id]["chat_history"])
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_client_info.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "product": val_product,
            "grateful": val_grateful,
            "ranting": val_ranting,
            "expression": val_expression,
            "civil": val_civil
        })

        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "sender": "representative",
            "receiver": "client",
            "message": response.strip(),
            "timestamp": timestamp
        })


    elif request.method == 'POST':
        prompt = request.json.get("prompt")
        client_id = request.json.get("client_id")
        show_info = request.json.get("show_info")
        show_emo = request.json.get("show_emo")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        result = sender_agent.invoke({"input": prompt, "chat_history": chat_history, "civil": session[session_id][client_id]["civil"]})
        response = result

        chat_history.extend([HumanMessage(content=prompt), AIMessage(content=response)])
        session[session_id][client_id]["chat_history"] = messages_to_dict(chat_history)

        turn_number = len(chat_history) // 2 + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number - 1,
            "sender": "client",
            "receiver": "representative",
            "message": prompt.strip(),
            "timestamp": timestamp
        })
        
        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "sender": "representative",
            "receiver": "client",
            "message": response.strip(),
            "timestamp": timestamp
        })

    return jsonify({
        "client": client_id,
        "message": response,
        "show_info": show_info,
        "show_emo": show_emo,
        "clientQueue": clientQueue

    })

@app.route('/<session_id>/update-clientQueue')
def update_client_queue(session_id):
    global clientQueue
    if not clientQueue:
        clientQueue = initQueue.copy()
    client = clientQueue.pop(0) 
    clientParam = f"?product={client['product']}&grateful={client['grateful']}&ranting={client['ranting']}&expression={client['expression']}&civil={client['civil']}&info={client['info']}&emo={client['emo']}"
    new_url = url_for('index', session_id=session_id) + clientParam

    return jsonify({"url": new_url})

@app.route('/<session_id>/get-emo-feedback', methods=['POST'])
def getEmoFeedback(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        rate = request.json.get("rate")
        support_type = request.json.get("type")

        turn_number = len(session[session_id][client_id]["chat_history"]) // 2
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        query = {
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": support_type
        }
        update = {
            "$set": {
                "client_feedback": rate,
                "timestamp_feedback": timestamp,
            }
        }

        res = chat_emo_feedback.update_one(query, update)
        if res == 0:
            return jsonify({"message": "No existing record found to update"}), 404
        return jsonify({"message": "Feedback received"}), 200
    return jsonify({"message": "Invalid session or session expired"}), 400


@app.route('/<session_id>/get-emo-support', methods=['POST'])
def getEmoSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        reply = request.json.get("client_reply")
        support_type = request.json.get("type")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        turn_number = len(chat_history) // 2 + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        if support_type==TYPE_EMO_REFRAME:
            response_cw_emo = emo_agent.invoke({'complaint':reply, "chat_history": chat_history})
            thought = response_cw_emo['thought']
            reframe = response_cw_emo['reframe']
        # Thought
            chat_emo_feedback.insert_one({
                "session_id": session_id,
                "client_id": client_id,
                "turn_number": turn_number,
                "support_type": "You might be thinking",
                "support_content": thought.strip(),
                "timestamp_arrival":timestamp
            })
        # Reframe
            chat_emo_feedback.insert_one({
                "session_id": session_id,
                "client_id": client_id,
                "turn_number": turn_number,
                "support_type": "Be Mindful of Your Emotions",
                "support_content": reframe.strip(),
                "timestamp_arrival": timestamp
            })
            return jsonify({
                "message": {
                    'thought':thought,
                    'reframe': reframe
                }
            })
        elif support_type==TYPE_EMO_SHOES:
            response_cw_emo = ep_agent.invoke({'complaint':reply, "chat_history": chat_history})
            response = response_cw_emo
            chat_emo_feedback.insert_one({
                "session_id": session_id,
                "client_id": client_id,
                "turn_number": turn_number,
                "support_type": "Put Yourself in the Client's Shoes",
                "support_content": response.strip(),
                "timestamp_arrival": timestamp
            })
            return jsonify({
                "message": response
            })
        else:
            return jsonify({"error": "Invalid support_type"}), 400

    return jsonify({"error": "Invalid session_id"}), 400

@app.route('/<session_id>/sentiment', methods=['POST'])
def sentiment(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        reply = request.json.get("client_reply")
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        turn_number = len(session[session_id][client_id]["chat_history"]) // 2 + 1

        # Perform sentiment analysis
        sentiment_category = analyze_sentiment(reply)

        chat_emo_feedback.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": "Sentiment Analysis",
            "support_content": sentiment_category,
            "timestamp_arrival": timestamp
        })

        return jsonify({'message': sentiment_category})
    else:
        return jsonify({"error": "Invalid session_id"}), 400



@app.route('/<session_id>/get-info-support', methods=['POST'])
def getInfoSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")

        reply = request.json.get("client_reply")
        # support_type = request.json.get("type")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        response_cw_info = info_agent.invoke({'product': session[session_id][client_id]["product"],'complaint':reply, "chat_history": chat_history})
        # response = response_cw_info.content

        return jsonify({
            "message": response_cw_info
        })

@app.route('/<session_id>/get-trouble-support', methods=['POST'])
def getTroubleSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        reply = request.json.get("client_reply")
        # support_type = request.json.get("type")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        response_cw_trouble = trouble_agent.invoke({'product': session[session_id][client_id]["product"],'complaint':reply, "chat_history": chat_history})
        response = "Troubleshooting Guide:\n" + response_cw_trouble

        return jsonify({
            "message": response
        })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
#%%
