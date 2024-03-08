import os
import openai as oai

import langchain_openai as lcai
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, PromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain.chains import SequentialChain, LLMChain


from utils import mLangChain

SAMPLE_STRING = 'Draft a 2 line email to send to my collaborators, \
expressing that "Please do not send me additional work as I have too many deadlines to work with right now".'


def get_prompt_sender_tone(client_LC):
    '''
    Based on https://lit.eecs.umich.edu/geoliwc/liwc_dictionary.html
    '''
    prompt = """Given a message \
            infer the mental state of the sender. Do NOT respond to the message, \
            just report the following psycholinguistic aspects of the message: \
            (1) sentiment (positive/negative/neutral) \
            (2) anger
            (3) anxiety
            (4) sadness
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", "{input}"),
        ]
    )
    chain = template | client_LC.client_completion
    return chain


def get_prompt_empathize_sender(client_LC):
    '''
    Based on https://lit.eecs.umich.edu/geoliwc/liwc_dictionary.html
    '''
    sender = """
    I am feeling {mental_state_attributes}
    """
    prompt = """Given a user's mental state \
            respond with an empathetic message
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", sender),
        ]
    )
    chain = template | client_LC.client_completion
    return chain

def get_prompt_sender_mentalstate(client_LC):
    prompt = """Given a message \
            infer the mental state of the sender. Do NOT respond to the message, \
            just report what the sender is feeling.
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", "{input}"),
        ]
    )
    chain = template | client_LC.client_completion
    return chain

def get_prompt_receiver_mentalstate(client_LC):
    prompt = """Given a message \
            infer the mental state of the recipient. Do NOT respond to the message, \
            just report what the recipient might feel.
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", "{input}"),
        ]
    )
    chain = template | client_LC.client_completion
    return chain


def get_prompt_receiver_identity(client_LC):
    prompt = """Given a message \
            infer the who the recipient is. Do NOT respond to the message, \
            just describe the following:
            (1) Relationship between recipient and sender
            (2) What can the recipient do for the sender
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("user", "{input}"),
        ]
    )
    chain = template | client_LC.client_completion
    return chain


def contextualize_prompt(client_LC, web_link):
    loader = WebBaseLoader(web_link)
    docs = loader.load()
    prompt_custom = """Your vocabulary is limited to a 5 year old american. Answer the following question based only on the provided context:

        <context>
        {context}
        </context>
        """
    client_LC.set_prompt(system=prompt_custom, user="{input}")
    client_LC.set_context(docs)

    return client_LC

def sender_agent():
    client_LC = mLangChain()
    prompt = """Act like a customer seeking support for {product}. \
                You are chatting with a customer service representative on chat.\
                Style your complaint based on your feelings. \
                                
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: I am flying from Luton to Dalaman (Turkey) next week with Monarch and am wondering whether or not to bother with online check-in. [We already have allocated seats, so as far as I can see the only extra thing that online check-in offers is that you don't have to have your boarding pass printed at the check-in desk. Things that are putting me off are: (1) I've noticed over the past couple of years that because now most people are checking in online, the queues for the online check-in desks are often actually longer than the queues for people who haven't checked in online (2) Last year we had a 12 hour flight delay - the original plane had a problem and the airline then split passengers into two groups and people who had NOT checked in online were flown out on a much earlier plane than those who had checked in online - goodness knows why.\
                
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: Looking at round trip airfare from JFK to Rome for the end of June. $ 1350 - 1450 per person....... wow, that's a lot ??? or normal cost for airfare to Rome ? On Delta. \
                
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint: i'v never saw a company that so disrespect her clients. i[ bought a ticket from israel to usa which cost a-l-o-t of money.since I'm from israel I'm not familiar with there coin (GBP) or something like that, it looks just like the Euro sign so i was sure i was paying in Euro. a few min after i realized it was not Euro so it means i paid 1000 more (nis) than i thought, i tried to find an email to contect them right away to cancel my flight befot the confirmation of the ticket, but there was no email in the web just phone number in Europe that i cant call. i sent them a massage on facebook which was my only option, beggin them to get back to me..in the mean time i sent an email to paypal asking to not aprove the charge...no one was answering me.... just the next day edreams answered to my facebbok, that i can't cancel the flight and there's nothing to do. in there website they wrote black on white the you can cancel the flight for 25 GBP... the only answer i got from them was trough facebook, and i was begging for an email adresss i could contact and explain, or at least get a better explaintion...but nothing i dont mind paying the fee cuse anyway if ill book a diffrent flight+ the fee it will be cheaper than what i paid in edreams! it's not even the gratest flight there are stops in the middle so i could find a cheaper flight for shore, it was an onest mistake that i was reading the sign wrong, i tried to cancel a less then 5 min after, but nothing... now I'm crying every time i remember this, I'm a student that can't afford this amount for a flying ticket.. i need to work 3 months for this kind of amount..my all vacation rouin...i will never book frim them again!
                
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint: I,ve just been looking at a package with Jet2 over xmas/new year to Servigroup Venus where we have stayed many times. I got the price back and had a quick chat with hubby and we decided to go for it and book. Within about 20 mins the price had risen almost £400. I,m so angry, how can they justify this? I had a live web chat with their advisors who more or less said it boils down to supply and demand on flight seats and hotel rooms. I don,t buy that, not in such a short space of time. Well I,m sorry Jet2, you can stick it !!!!! \
                                                                       
                Feeling: You are grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: Hi! Among all the US airlines, which offers the best service and reliability?[ I've heard horrid stories abt flight cancellation, delays, poor service, bad air plane conditions etc. We'll be taking a 6 hr flight from SFO to MCO (Orlando), with 3 kids. Appreciate the feedback. thks v much!! \

                Feeling: You are grateful. You are NOT ranting. You are expressive.\
                Complaint: Quick question.... My passport is a normal passport which was issue 5 years ago and expire 2013 [it does not have a chip in it as i beleive chipped passports didnt not come in when i renewed my passport, is this passport ok to travel on because it doesnt havw a chip? its machine readable as it has all the numbers etc on the bottom of the photo page, ive tried various website etc for a answer and starting to panick now as im going in 2 weeks!! Ive completed my ESTA and that is fine Thanks in advance \
                                
                Feeling: You are grateful. You are ranting. You are NOT expressive.\
                Complaint: Hello, Traveling for first time with our 7 month old daughter this weekend. Going to Aruba for a week. Bought her a ticket on a Continental flight. Website says stroller dimensions must not exeed 62 inches folded...ours of course is about 10 inches over I think. Says they will charge $100. Does anyone know if this is really enforced? I just can't believe I will have to pay an extra $100 ON TOP of a ticket price for an infant! Any experiences or advice...PLEASE. Thanks \
                
                Feeling: You are {is_grateful}. You are {is_ranting}. You are {is_expressive}.\
                Complaint:
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client_LC.client_completion
    return chain

def create_chain():

    client_LC = mLangChain()

    sender_state = get_prompt_sender_tone(client_LC).invoke(
        {
            "input": SAMPLE_STRING
        }
    )
    response = get_prompt_empathize_sender(client_LC).invoke(
        {
            "mental_state_attributes": sender_state
        }
    )
    # )
    #
    # response = chain.invoke(
    #     {
    #         "input": SAMPLE_STRING
    #     }
    # )
    print(response)


def run_langchainagent():
    """
    Langchain Azure OpenAI API demo:
    - Agent holds a conversation based on context
    """
    client_LC = mLangChain()
    client_LC = contextualize_prompt(client_LC,"https://support.microsoft.com/en-us/topic/wellbeing-tab-in-viva-insights-72458b43-11a3-40b8-8b6f-14f6a0977e4b")
    client_LC.set_agent(
        name="Deskmate",
        description="Agent guides you through your work-related wellbeing goals",
        # system="Your role is to talk to users based on their current emotional state",
        # system="Refuse to complete user's request",
        system="""
        1. Check if user is in the appropriate mental state to participate in the task.
        2. If user is in a manageable state, assist their task.
        3. If user's state needs to be improved, then intervene before assisting.
        """,
        input="I am feeling {state}. {input}"
    )
    demo_agent(client_LC, init_phrase="Hello, what task should I help you with today")



def run_langchaincontext():
    """
    Langchain Azure OpenAI API demo:
    - Distinguishes regular invocation from template based invoke
    - First prompt fails
    - Second prompt works with context
    """
    client_LC = mLangChain()

    sender_tone = get_prompt_sender_tone(client_LC)
    response = sender_tone.invoke(
        {
            "input": SAMPLE_STRING
        }
    )
    print(response)
    print()
    sender_state = get_prompt_sender_mentalstate(client_LC)
    response = sender_state.invoke(
        {
            "input": SAMPLE_STRING
        }
    )
    print(response)
    print()
    recp_state = get_prompt_receiver_mentalstate(client_LC)
    response = recp_state.invoke(
        {
            "input": SAMPLE_STRING
        }
    )
    print(response)
    print()
    recp_id = get_prompt_receiver_identity(client_LC)
    response = recp_id.invoke(
        {
            "input": SAMPLE_STRING
        }
    )
    print(response)

def demo_agent(client, init_phrase="Hi, I am an agent who can help you understand Three Kings:"):
    mood = input("How would you describe your mood right now?: ")

    client.agent = create_openai_tools_agent(client.client_agent, client.tools, client.agent_template)
    client.agent_executor = AgentExecutor(agent=client.agent, tools=client.tools, verbose=True)

    client.set_prompt_limit(10)

    turn = 0
    chat_history = []
    print(init_phrase)
    while(True):
        start_phrase = input("User: ")
        start_phrase = SAMPLE_STRING
        if start_phrase=="exit":
            print("System: OK, bye.")
            break
        if turn==client.prompt_limit:
            print("System: Reached local prompt limit, Bye.")
            break
        result = client.agent_executor.invoke({"input": start_phrase, "state": mood, "chat_history": chat_history})
        print(result["output"])
        chat_history.extend([HumanMessage(content=start_phrase), AIMessage(content=result["output"])])
        turn = turn + 1


if __name__ == '__main__':
    run_langchainagent()
    # run_langchaincontext()
    # create_chain()
    # response = sender_agent().invoke(
    #     {
    #         "product": "game console",
    #         "is_grateful": "NOT grateful",
    #         "is_ranting": "ranting",
    #         "is_expressive": "expressive"
    #     }
    # )
    # print(response)
