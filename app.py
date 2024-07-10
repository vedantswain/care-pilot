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

from sentiment import analyze_sentiment_transformer, analyze_sentiment_decision

import config as common

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
chat_post_task = db.chat_post_task
chat_history_collection = db.chat_history
chat_client_info = db.chat_client_info
chat_in_task = db.chat_in_task
chat_pre_task = db.chat_pre_task


sender_agent = None
chat_history = [
]

# clientQueue = common.randomQueue.copy()
clientQueue = []



sender_initial = agent_sender_fewshot_twitter_categorized()
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

@app.route('/launch')
def launch():
    return render_template('launch.html')

@app.route('/chat/<scenario>/')
def start_chat(scenario):
    global clientQueue
    if not clientQueue:
        # clientQueue = common.randomQueue
        clientQueue = common.get_study_queue(scenario)
    # random.shuffle(clientQueue)
    client = clientQueue.pop(0)
    session_id = str(uuid4())   ### unique to each user/participant/representative
    current_client = client['name']
    session[session_id] = {}
    session[session_id]['current_client'] = current_client
    session[session_id]['client_queue'] = clientQueue

    clientParam = f"?name={client['name']}&domain={client['domain']}&category={client['category']}&grateful={client['grateful']}&ranting={client['ranting']}&expression={client['expression']}&civil={client['civil']}&info={client['info']}&emo={client['emo']}"
    #

    return redirect(url_for('getPreSurvey', session_id=session_id) + clientParam)

# End-point to test the pre-survey HTML
@app.route('/<session_id>/pre-task-survey')
def getPreSurvey(session_id):
    return render_template('pre_task_survey.html', session_id=session_id)

@app.route('/<session_id>/store-pre-task-survey', methods=['POST'])
def storePreSurvey(session_id):


    if session_id in session:

        data = request.get_json()
        clientParam = "?"+data['client_param']

        for k in data:  # Convert string values into integers

            if k != "client_param":
                data[k] = int(data[k])

        if not data:
            return jsonify({"message": "No data received"}), 400

        data['session_id'] = session_id
        data['timestamp'] = datetime.datetime.now(datetime.timezone.utc)

        try:
            result = chat_pre_task.insert_one(data)
            if result.inserted_id:
                jsoninfo = {
                    "message": "Survey data saved successfully",
                    "id": str(result.inserted_id)
                }
                return redirect(url_for('index', session_id=session_id) + clientParam, 302, jsoninfo)
            else:
                return jsonify({"message": "Failed to save data"}), 500
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": "Invalid session or session expired"}), 400


@app.route('/<session_id>/')
def index(session_id):
    if session_id in session:
        current_client = session[session_id]['current_client']
    else:
        current_client = 'Guest'

    return render_template('index_chat.html', session_id=session_id, current_client=current_client, common_strings=common.SUPPORT_TYPE_STRINGS)


@app.route('/<session_id>/get-reply', methods=['GET','POST'])
def getReply(session_id):
    clientQueue = session[session_id]['client_queue']
    if request.method == 'GET':
        val_name = request.args.get('name')
        val_domain = request.args.get('domain')
        val_category = request.args.get('category')
        val_grateful = request.args.get('grateful')
        val_ranting = request.args.get('ranting')
        val_expression = request.args.get('expression')
        val_civil = request.args.get('civil')
        show_info = request.args.get('info')
        show_emo = request.args.get('emo')

        complaint_parameters = {
            "domain": val_domain,
            "category": val_category,
            "is_grateful": 'grateful' if val_grateful==0 else 'NOT grateful',
            "is_ranting": 'ranting' if val_ranting==0 else 'NOT ranting',
            "is_expression": 'expression' if val_expression==0 else 'NOT expression'
        }

        response = sender_initial.invoke(complaint_parameters)

        client_id = str(uuid4())
        current_client = session[session_id]['current_client']
        session[session_id][client_id] = {"current_client": current_client, "domain": val_domain, "category": val_category, "civil": val_civil, "chat_history": []}
        session[session_id][client_id]["chat_history"] = messages_to_dict([AIMessage(content=response)])
        

        turn_number = len(session[session_id][client_id]["chat_history"])
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_client_info.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "client_name":val_name,
            "domain": val_domain,
            "category": val_category,
            "grateful": val_grateful,
            "ranting": val_ranting,
            "expression": val_expression,
            "civil": val_civil,
            "emo": show_emo
        })

        # Inserting first complaint message
        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "sender": "client",
            "receiver": "representative",
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

        # Insert representative response
        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number - 1,
            "sender": "representative",
            "receiver": "client",
            "message": prompt.strip(),
            "timestamp": timestamp
        })

        # Insert client reply to the response
        chat_history_collection.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "sender": "client",
            "receiver": "representative",
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
    clientQueue = session[session_id]['client_queue']
    client = clientQueue.pop(0)
    current_client = client['name']
    session[session_id]['current_client'] = current_client
    session[session_id]['client_queue'] = clientQueue

    clientParam = f"?name={client['name']}&domain={client['domain']}&category={client['category']}&grateful={client['grateful']}&ranting={client['ranting']}&expression={client['expression']}&civil={client['civil']}&info={client['info']}&emo={client['emo']}"
    new_url = url_for('index', session_id=session_id) + clientParam

    return jsonify({"url": new_url})

# End-point to test the survey HTML
@app.route('/<session_id>/post-task-survey')
def getSurvey(session_id):
    return render_template('feedback.html', session_id=session_id)

@app.route('/<session_id>/store-survey', methods=['POST'])
def storePostSurvey(session_id):
    if session_id in session:
        data = request.get_json()
        reverseLabels = ["support_effective", "support_helpful", "support_beneficial",
                         "support_adequate", "support_sensitive", "support_caring",
                         "support_understanding", "support_supportive"]
        for k in data:  # Convert string values into integers

            if k != "client_id":
                data[k] = int(data[k])

            if k in reverseLabels:
                data[k] = data[k] * (-1)
                
        if not data:
            return jsonify({"message": "No data received"}), 400

        data['session_id'] = session_id
        data['timestamp'] = datetime.datetime.now(datetime.timezone.utc)

        try:
            result = chat_post_task.insert_one(data)
            if result.inserted_id:
                return jsonify({"message": "Survey data saved successfully", "id": str(result.inserted_id)}), 200
            else:
                return jsonify({"message": "Failed to save data"}), 500
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": "Invalid session or session expired"}), 400

@app.route('/<session_id>/store-trouble-feedback',methods=['POST'])
def storeTroubleFeedback(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        rating = int(request.json.get("rate")) * -1
        support_type = request.json.get ("type")

        turn_number = len(session[session_id][client_id]["chat_history"])//2+1
        timestamp = datetime.datetime.now(datetime.timezone.utc)
    
        query = {
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": support_type
        }
        update = {
            "$set":{
                "user_feedback": rating,
                "timestamp_feedback": timestamp,
            }
        }
        res = chat_in_task.update_one(query, update)
        if res == 0:
            return jsonify({"message": "No existing record found to update"}), 404
        return jsonify({"message": "Trouble feedback received"}), 200
    return jsonify({"message": "Invalid session or session expired"}), 400
   
    

@app.route('/<session_id>/store-emo-feedback', methods=['POST'])
def storeEmoFeedback(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        rating = int(request.json.get("rate")) * -1    # helpful-unhelpful scale is reversed
        support_type = request.json.get("type")

        turn_number = len(session[session_id][client_id]["chat_history"]) // 2 + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        query = {
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": support_type
        }
        update = {
            "$set": {
                "user_feedback": rating,
                "timestamp_feedback": timestamp,
            }
        }

        res = chat_in_task.update_one(query, update)
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

        if support_type=="TYPE_EMO_REFRAME":
            response_cw_emo = emo_agent.invoke({'complaint':reply, "chat_history": chat_history})
            thought = response_cw_emo['thought']
            reframe = response_cw_emo['reframe']
            # Thought
            chat_in_task.insert_one({
                "session_id": session_id,
                "client_id": client_id,
                "turn_number": turn_number,
                "support_type": "TYPE_EMO_THOUGHT",
                "support_content": thought.strip(),
                "timestamp_arrival":timestamp
            })
            # Reframe
            chat_in_task.insert_one({
                "session_id": session_id,
                "client_id": client_id,
                "turn_number": turn_number,
                "support_type": "TYPE_EMO_REFRAME",
                "support_content": reframe.strip(),
                "timestamp_arrival": timestamp
            })
            return jsonify({
                "message": {
                    'thought':thought,
                    'reframe': reframe
                }
            })
        elif support_type=="TYPE_EMO_SHOES":
            response_cw_emo = ep_agent.invoke({'complaint':reply, "chat_history": chat_history})
            response = response_cw_emo
            chat_in_task.insert_one({
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
        # sentiment_category = analyze_sentiment_transformer(reply)
        sentiment_category = analyze_sentiment_decision(reply)

        chat_in_task.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": "TYPE_SENTIMENT",
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

        response_cw_info = info_agent.invoke({'domain': session[session_id][client_id]["domain"],'complaint':reply, "chat_history": chat_history})
        # response = response_cw_info.content

        turn_number = len(chat_history) // 2 + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc)


        chat_in_task.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": "TYPE_INFO_CUE",
            "support_content": response_cw_info,
            "timestamp_arrival": timestamp
        })
        return jsonify({
            "message": response_cw_info
        })
    return jsonify({"message": "Invalid session or session expired"}), 400


@app.route('/<session_id>/get-trouble-support', methods=['POST'])
def getTroubleSupport(session_id):
    if session_id in session:
        client_id = request.json.get("client_id")
        reply = request.json.get("client_reply")
        # support_type = request.json.get("type")

        retrieve_from_session = json.loads(json.dumps(session[session_id][client_id]["chat_history"]))
        chat_history = messages_from_dict(retrieve_from_session)

        response_cw_trouble = trouble_agent.invoke({'domain': session[session_id][client_id]["domain"],'complaint':reply, "chat_history": chat_history})
        response = "Troubleshooting Guide:\n" + response_cw_trouble

        turn_number = len(chat_history) // 2 + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        chat_in_task.insert_one({
            "session_id": session_id,
            "client_id": client_id,
            "turn_number": turn_number,
            "support_type": "TYPE_INFO_GUIDE",
            "support_content": response,
            "timestamp_arrival": timestamp
        })

        return jsonify({
            "message": response
        })
    return jsonify({"message": "Invalid session or session expired"}), 400

@app.route('/conversation_history')
def conversation_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return "Session ID is missing", 400
    return render_template('conversation_history.html', session_id=session_id)

@app.route('/complete')
def complete():
    return render_template('complete.html')

@app.route('/history/<session_id>/<client_id>')
def getClientHistory(session_id, client_id):
    chat_history = list(chat_history_collection.find({"session_id": session_id, "client_id": client_id}, {"_id": 0}))
    return jsonify({"chat_history": chat_history})

@app.route('/history/<session_id>')
def getClientList(session_id):
    clients_info = list(chat_client_info.find({"session_id": session_id}, {"_id": 0, "client_name": 1, "client_id": 1, "category":1}))
    return jsonify({"chat_history": chat_history, "clients_info": clients_info})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
#%%








