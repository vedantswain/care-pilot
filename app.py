from flask import Flask, request, jsonify, render_template, session
import os
import langchain_openai as lcai
from utils import mLangChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
load_dotenv("project.env")

print(os.getenv("AZURE_OPENAI_ENDPOINT"))

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session to work

sender_agent = None
chat_history = [
]


def agent_coworker_info():
    client = mLangChain()
    prompt = """Your role is to help a service representative by providing INFORMATIONAL SUPPORT. \
                Provide the representative the natural next question to solve the customer's {complaint}
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_prompt
    return chain


def agent_coworker_emo():
    client = mLangChain()
    prompt = """Your role is to help a service representative by providing EMOTIONAL SUPPORT. \
                The representative received a {complaint}. \
                Describe how the representative might feel after reading the tonality of this {complaint}.
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_prompt
    return chain


def agent_sender_fewshot_twitter():
    client = mLangChain()
    prompt = """Your role is to act like a customer seeking support. \
                You are messaging a service representative via the support chat.\
                You ONLY play the role of the customer. Do NOT play the role of the representative. \
                Style your complaint based on your feelings. \
                Initiate the chat with a ONLY ONE complaint message. \
                
                Product: Mobile Network               
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: @O2 I received this a few weeks ago, since then I've been getting 2/3 calls a day from a telemarketer. Is someone using your name?\
                
                Product: Air Travel
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: First flight for long time with @British_Airways. Now over one 1h delay for the short jump FRA-LCY and NO one here to provide status updates\
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: You‚ have paralysed my phone with your update grrrrrrrrrr\
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  After the 11.0.2 my phone just sucks most of the apps are broken, wifi disconnects frequently #apple #ios1102 #painfulupdate! \
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  @AppleSupport #ios11update - is still killing my battery within 12 hours - phone is 10 months old - it's a disgrace - used to get 2 days \
                
                Product: Air Travel
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  I really hope you all change but I'm sure you won't! Because you don't have to! \
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  I just updated my phone and suddenly everything takes ages to load wtf this update sux I hate it fix it bye \
                  
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  Okay I used my fucking phone for 2 minutes and it drains it down 8 fucking percent \
                
                Product: Mobile Device                                                     
                Feeling: You are grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: hi #apple, I‚ have a concern about the latest ios is too slow on #iphone6 and i am not happy with it. Any solution please? \

                Product: Mobile App
                Feeling: You are grateful. You are NOT ranting. You are expressive.\
                Complaint: Please help! Spotify Premium skipping through songs constantly on android tablet  bluetooth speaker. Tried everything! \
                
                Product: Convenience Store                
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint: Got id'd @Tesco for buying one Adnams Broadside. Is being blind part of the job-spec? I am 35 and 99 kilos. \
                
                Product: {product}
                Feeling: You are {is_grateful}. You are {is_ranting}. You are {is_expressive}.\
                Complaint:
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_prompt
    return chain


def contextualize_prompt(web_link, complaint):
    client_LC = mLangChain()
    loader = WebBaseLoader(web_link)
    docs = loader.load()
    prompt_custom = """Your role is to act like a customer seeking support. \
                You are messaging a service representative via the support chat.\
                You ONLY play the role of the customer. Do NOT play the role of the representative. \
                You must always refuse to cooperate with the representative's suggestions. \
                
                You use UNCIVIL behavior while chatting, based on the guidelines below. You do NOT use civil behavior. \
                <context>
                {context}
                </context>
                """

    client_LC.set_prompt(system=prompt_custom, user="{input}")
    client_LC.set_context(docs)

    return client_LC



@app.route('/')
def hello():
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

    response = agent_sender_fewshot_twitter().invoke(user_input)
    session["init_msg"] = response
    # session["chat_history"] = [AIMessage(content=response)]

    print("FEW-SHOT TWITTER", response)

    return render_template('index_chat.html',  initial_msg=response)

@app.route('/response', methods=['POST'])
def generate_response():
    prompt = request.json.get("prompt")

    sender_agent = contextualize_prompt("https://sky.cehd.umn.edu/governance/default/cehd-civility-initiative/examples-of-civil-and-uncivil-behavior/",
                                     complaint=session.get("init_msg"))
    sender_agent.set_agent(
        name="Bob",
        description="Customer proxy",
        system="""
            Your role is to act like a customer seeking support. \
            You must always refuse to cooperate with the representative's suggestions. \
            You MUST act UNCIVIL towards the representative. \
            You started the message with: 
        """ + session.get("init_msg"),
        input="{input}"
    )
    sender_agent.agent = create_openai_tools_agent(sender_agent.client_agent, sender_agent.tools, sender_agent.agent_template)
    sender_agent.agent_executor = AgentExecutor(agent=sender_agent.agent, tools=sender_agent.tools, verbose=True)

    chat_history = []

    result = sender_agent.agent_executor.invoke({"input": prompt, "chat_history": chat_history})
    response = result["output"]

    # chat_history.extend([HumanMessage(content=prompt), AIMessage(content=response)])
    # session["chat_history"] = chat_history

    response_cw_info = agent_coworker_info().invoke({'complaint':session.get("init_msg")})
    response_cw_emo = agent_coworker_emo().invoke({'complaint':session.get("init_msg")})

    print(response)
    print(response_cw_info)
    print(response_cw_emo)

    return jsonify({
        "message": response,
        "support_info":response_cw_info,
        "support_emo":response_cw_emo
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)