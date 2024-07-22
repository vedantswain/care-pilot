from dotenv import load_dotenv
import pandas as pd
import os
import openai as oai
import langchain_openai as lcai
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import agents as mAgents
sender_initial = mAgents.agent_sender_fewshot_twitter_categorized()
sender_agent = mAgents.mAgentCustomer()

# Load environment variables
load_dotenv("project.env")

def agent_representative():
    support_agent_prompt = """
    You are a service representative chatting with a customer online.\
    You need to address the customer's complaint without escalating the issue to a supervisor.\
    Given the chat history, respond professionally to the customer's complaint: {message}.\
    Ensure the response is concise and limited to 2 sentences, containing all relevant information.
    """

    template = ChatPromptTemplate.from_messages(
        [
            ("system", support_agent_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{message}"),
        ]
    )

    chain = (RunnablePassthrough.assign(
        context=mAgents.get_historical_context_chain()
    )
             | template
             | mAgents.llminfo
             )

    chain = chain | StrOutputParser()

    return chain



follow_up_prompt = """
The customer has received a response from the support agent. Generate a follow-up complaint or question from the customer: {support_agent_response}. Ensure the follow-up complaint is concise and limited to 2 sentences, containing all relevant information.
"""

final_response_prompt = """
You are a customer support agent. Respond professionally to the customer's follow-up complaint or question: {follow_up_complaint}. Ensure the response is concise and limited to 2 sentences, containing all relevant information.
"""

# Create templates
def generate_initial_complaint(val_domain, val_category):
    complaint_parameters = {
        "domain": val_domain,
        "category": val_category,
        "is_grateful": 'NOT grateful',
        "is_ranting": 'ranting',
        "is_expression": 'expressive'
    }

    initial_complaint = sender_initial.invoke(complaint_parameters)
    return initial_complaint


# Function to generate scenarios
def generate_scenarios(domains, categories, examples_per_pair):
    scenarios = []

    iteration = 1
    for domain in domains:
        for category in categories:
            for _ in range(examples_per_pair):
                print(f"Generating scenario {iteration}")
                iteration += 1          
                
                # Generate initial complaint
                initial_complaint = generate_initial_complaint(domain, category)
                chat_history = [AIMessage(content="Client: "+initial_complaint)]


                # Generate support agent response
                support_agent_response1 = agent_representative().invoke({"chat_history": chat_history, "message": initial_complaint, "sender":"client"})
                chat_history.extend([HumanMessage(content="Representative: "+support_agent_response1)])


                # Generate follow-up complaint
                follow_up_complaint1 = sender_agent.invoke({"input": support_agent_response1, "chat_history": chat_history, "civil": 0})
                chat_history.extend([AIMessage(content="Client: "+follow_up_complaint1)])


                # Generate support agent response
                support_agent_response2 = agent_representative().invoke({"chat_history": chat_history, "message": initial_complaint, "sender":"client"})
                chat_history.extend([HumanMessage(content="Representative: "+support_agent_response2)])


                # Generate follow-up complaint
                follow_up_complaint2 = sender_agent.invoke({"input": support_agent_response2, "chat_history": chat_history, "civil": 0})
                chat_history.extend([AIMessage(content="Client: "+follow_up_complaint2)])


                # Store scenario
                scenarios.append({
                    "Category": category,
                    "Domain": domain,
                    "Initial Complaint": initial_complaint,
                    "Support Agent Response 1": support_agent_response1,
                    "Follow-up Complaint 1": follow_up_complaint1,
                    "Support Agent Response 2": support_agent_response2,
                    "Follow-up Complaint 2": follow_up_complaint2
                })

    return scenarios


# Generate scenarios
domains = ["mobile-device", "hotel", "airlines"]
categories = mAgents.categories.keys()
scenarios = generate_scenarios(domains, categories, examples_per_pair=3)

df = pd.DataFrame(scenarios)
df.to_csv("/Users/jashparekh/Desktop/scenarios_using_twitter_examples.csv", index=False)

print("scenarios_using_twitter_examples.csv")