from flask import Flask, request, jsonify, render_template, session
import os, json
import certifi
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
load_dotenv("project.env")

DB_NAME = "test"

print(os.getenv("AZURE_OPENAI_ENDPOINT"))

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session to work
# app.config["MONGO_URI"] = os.getenv("AZURE_COSMOS_MONGO_CONNSTRING")
# mongo = PyMongo(app, tlsCAFile=certifi.where())
# client = mongo.cx

# db = client[DB_NAME]
# print(client.list_databases())

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
    return render_template('index_chat.html')

@app.route('/get-reply', methods=['GET','POST'])
def getReply():

    if request.method == 'GET':
        # Handle GET request
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
        session["product"] = val_product
        session["chat_history"] = messages_to_dict([AIMessage(content=response)])

    elif request.method == 'POST':
        prompt = request.json.get("prompt")

        retrieve_from_session = json.loads(json.dumps(session["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        result = sender_agent.invoke({"input": prompt, "chat_history": chat_history})
        response = result

        chat_history.extend([HumanMessage(content=prompt), AIMessage(content=response)])
        session["chat_history"] = messages_to_dict(chat_history)

    return jsonify({
        "message": response
    })


@app.route('/get-emo-support', methods=['POST'])
def getEmoSupport():
    reply = request.json.get("client_reply")
    support_type = request.json.get("type")

    retrieve_from_session = json.loads(json.dumps(session["chat_history"]))
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


@app.route('/get-info-support', methods=['POST'])
def getInfoSupport():
    reply = request.json.get("client_reply")
    # support_type = request.json.get("type")

    retrieve_from_session = json.loads(json.dumps(session["chat_history"]))
    chat_history = messages_from_dict(retrieve_from_session)

    response_cw_info = info_agent.invoke({'product': session['product'],'complaint':reply, "chat_history": chat_history})
    # response = response_cw_info.content

    return jsonify({
        "message": response_cw_info
    })

@app.route('/get-trouble-support', methods=['POST'])
def getTroubleSupport():
    reply = request.json.get("client_reply")
    # support_type = request.json.get("type")

    retrieve_from_session = json.loads(json.dumps(session["chat_history"]))
    chat_history = messages_from_dict(retrieve_from_session)

    response_cw_info = trouble_agent.invoke({'product': session['product'],'complaint':reply, "chat_history": chat_history})
    response = "Troubleshooting Guide:\n" + response_cw_info

    return jsonify({
        "message": response
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
#%%
