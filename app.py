from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os, json
import certifi
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

from dotenv import load_dotenv
from uuid import uuid4
import datetime
import redis
from flask_session import Session
load_dotenv("project.env")

DB_NAME = "test"

print(os.getenv("AZURE_OPENAI_ENDPOINT"))

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session to work
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

sender_agent = None
chat_history = [
]


sender_initial = agent_sender_fewshot_twitter()
sender_agent = mAgentCustomer()
emo_agent = mAgentER()
ep_agent = mAgentEP()
info_agent = mAgentInfo()
trouble_agent = mAgentTrouble()


@app.route('/')
def hello():
    session_id = str(uuid4())
    session[session_id] = {}
    return redirect(url_for('index', session_id=session_id))

@app.route('/<session_id>/')
def index(session_id):
    return render_template('index_chat.html', session_id=session_id)


@app.route('/<session_id>/get-reply', methods=['GET','POST'])
def getReply(session_id):
    if request.method == 'GET':
        val_product = request.args.get('product')
        val_grateful = request.args.get('grateful')
        val_ranting = request.args.get('ranting')
        val_expressive = request.args.get('expressive')

        user_input = {
            "product": val_product,
            "is_grateful": 'grateful' if val_grateful==0 else 'NOT grateful',
            "is_ranting": 'ranting' if val_ranting==0 else 'NOT ranting',
            "is_expressive": 'expressive' if val_expressive==0 else 'NOT expressive'
        }

        response = sender_initial.invoke(user_input)
        
        client_id = str(uuid4())
        session[session_id] = {client_id: {"product": val_product, "chat_history": []}}
        session[session_id][client_id]["chat_history"] = messages_to_dict([AIMessage(content=response)])
        print("here get", session[session_id][client_id])
        

        turn_number = len(session[session_id][client_id]["chat_history"])
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_history_collection.insert_one({
            "session_id": session_id,
            "turn_number": turn_number,
            "sender": "representative",
            "message": response.strip(),
            "timestamp": timestamp
        })


    elif request.method == 'POST':
        prompt = request.json.get("prompt")
        client_id = request.json.get("client_id")

        print("here getp", client_id)
        print("here getp", session[session_id][client_id]["product"])

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        result = sender_agent.invoke({"input": prompt, "chat_history": chat_history})
        response = result

        chat_history.extend([HumanMessage(content=prompt), AIMessage(content=response)])
        session[session_id][client_id]["chat_history"] = messages_to_dict(chat_history)

        turn_number = len(chat_history)
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_history_collection.insert_one({
            "session_id": session_id,
            "turn_number": turn_number - 1,
            "sender": "client",
            "message": prompt.strip(),
            "timestamp": timestamp
        })
        
        chat_history_collection.insert_one({
            "session_id": session_id,
            "turn_number": turn_number,
            "sender": "representative",
            "message": response.strip(),
            "timestamp": timestamp
        })

    return jsonify({
        "client": client_id,
        "message": response
    })


@app.route('/<session_id>/get-emo-support', methods=['POST'])
def getEmoSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")

        print("here emo", client_id)
        print("here emo", session[session_id][client_id]["product"])
        
        reply = request.json.get("client_reply")
        support_type = request.json.get("type")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        if support_type=="You might be thinking":
            response_cw_emo = emo_agent.invokeThought({'complaint':reply, "chat_history": chat_history})
            response = response_cw_emo
        if support_type=="Put Yourself in the Client's Shoes":
            response_cw_emo = ep_agent.invoke({'complaint':reply, "chat_history": chat_history})
            response = response_cw_emo
        if support_type=="Be Mindful of Your Emotions":
            response_cw_emo = emo_agent.invoke({'complaint':reply, "chat_history": chat_history})
            response = response_cw_emo
            
        return jsonify({
            "message": response
        })


@app.route('/<session_id>/get-info-support', methods=['POST'])
def getInfoSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")

        print("here info", client_id)
        print("here info", session[session_id][client_id]["product"])

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
        print("here trouble", client_id)
        print("here trouble", session[session_id][client_id]["product"])
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
