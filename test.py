import time
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

product = "pizza"
fixed_complaint = "Do I look like I memorize every insignificant number? It's your job to fix this, not mine. Here, since you can't seem to do it yourself: 85692347. Happy now?"
chat_history = [AIMessage(content="""@Dominos I ordered a pizza from you guys and it arrived cold and soggy. Not the delicious meal I was hoping for. Disappointed and hungry."""), HumanMessage(content="Sorry, could you please share your order number?")]
input_data_product = [product, fixed_complaint, chat_history]
input_data = [None, fixed_complaint, chat_history]

def test_agent_performance(agent_function, input_data, num_calls=100):
    total_time = 0
    for _ in range(num_calls):
        start_time = time.time()
        if input_data[0] == None:
            res = agent_function.invoke({'complaint': input_data[1], 'chat_history': input_data[2]})
        else:
            res = agent_function.invoke({'product': input_data[0], 'complaint': input_data[1], 'chat_history': input_data[2]})
        end_time = time.time()
        print(res)
        total_time += (end_time - start_time)
    average_time = total_time / num_calls
    return average_time


info_agent1_avg_time = test_agent_performance(agent_coworker_info(), input_data_product)
emo_agent = mAgentER()
emo_reframe_agent1_avg_time = test_agent_performance(emo_agent, input_data)
emo_perspec_agent1_avg_time = test_agent_performance(agent_coworker_emo_perspective(), input_data)
trouble_agent1_avg_time = test_agent_performance(agent_coworker_trouble(), input_data_product)

# Output the results
print(f"Info Agent 1 Average Time: {info_agent1_avg_time}")
print(f"Emo Reframe Agent 1 Average Time: {emo_reframe_agent1_avg_time}")
print(f"Emo Perspec Agent 1 Average Time: {emo_perspec_agent1_avg_time}")
print(f"Trouble Agent 1 Average Time: {trouble_agent1_avg_time}")

# Flask
# Info Agent 1 Average Time: 6.202272715568543
# Emo Reframe Agent 1 Average Time: 1.5193539357185364
# Emo Perspec Agent 1 Average Time: 4.14248565196991
# Trouble Agent 1 Average Time: 4.30497807264328


# Python
# Info Agent 1 Average Time: 6.003182413578034
# Emo Reframe Agent 1 Average Time: 1.5507910704612733
# Emo Perspec Agent 1 Average Time: 3.645583713054657
# Trouble Agent 1 Average Time: 3.880960552692413