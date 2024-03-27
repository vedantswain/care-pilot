import os

from langchain.schema import messages_from_dict, messages_to_dict

import langchain_openai as lcai
from utils import mLangChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import re
from dotenv import load_dotenv
load_dotenv("project.env")

embeddings = lcai.AzureOpenAIEmbeddings(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    openai_api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment="TEST-Embedding",
)

llmchat = lcai.AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="NUHAI-GPT4",
    openai_api_version="2024-02-15-preview",
    model_name="gpt-4",
)
llminfo = lcai.AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="NUHAI-GPT4",
    openai_api_version="2024-02-15-preview",
    model_name="gpt-4",
    temperature=0.1
)

def get_historical_info_context_chain():
    contextualize_q_system_prompt = """Given a chat history and the latest user input \
        which might reference context in the chat history, formulate a standalone statement \
        which can be understood without the chat history. Do NOT respond to the statement, \
        just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{complaint}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | llmchat | StrOutputParser()
    return contextualize_q_chain

def agent_coworker_info():
    client = mLangChain()
    prompt = """Your role is to help a service representative by providing INFORMATIONAL SUPPORT. \
                The representative is chatting online with a customer complaining about {product}.  \
                
                Given the chat history,
                provide 2-3 hints to help the representative's response.\
                The hints should direct the representative to do ONLY ONE of the following:\
                
                1) Inquire more details about the problem. OR \
                2) Request the customer to troubleshoot. OR \
                3) Provide a solution to resolve the customer's need. \
                
                Each cue should be a single phrase of less than 10 words.\
                Do NOT number the cues.\
                
                Customer message: {complaint}
                Hints: 
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{product}: {complaint}"),
        ]
    )
    chain = template | client.client_completion

    chain = (RunnablePassthrough.assign(
        context=get_historical_info_context_chain()
    )
             | template
             | llminfo
             )
    
    def extract_cues(chain_output):
        cues_text = chain_output.content
        # Assuming each cue is separated by a newline in the chain_output.
        cues = cues_text.split('\n')
        # Filter out any empty strings or whitespace-only strings
        cues = [cue.strip() for cue in cues if cue.strip()]
        # Return the first 2 - 3 cues
        processed_cues = [re.sub(r'^\d+\.\s*', '', cue) for cue in cues]
        return processed_cues[:3]
    
    chain = chain | extract_cues

    return chain


def agent_coworker_trouble():
    client = mLangChain()
    prompt = """Your role is to help a service representative by providing PROCEDURAL SUPPORT. \
                The representative is chatting online with a customer complaining about {product}. \
                Given the chat history,
                list 3-7 steps to guide the representative in resolving the customer complaint.\

                Do NOT include steps that have already been tried.\
                Every step should be less than 10 words.\
                
                Customer message: {complaint}
                Troubleshooting Steps: 
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{product}: {complaint}"),
        ]
    )
    chain = template | client.client_completion

    chain = (RunnablePassthrough.assign(
        context=get_historical_info_context_chain()
    )
             | template
             | client.client_completion
             )

    return chain


def agent_coworker_emo():
    client = mLangChain()
    prompt = """Your role is to help a service representative by providing EMOTIONAL SUPPORT. \
                The representative received a {complaint}. \
                Describe how the representative might feel after reading the tonality of this {complaint}. \
                
                Mood:\
                Stress-level:\
                Work-load:\
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_completion
    return chain

def agent_coworker_emo_perspective():
    client = mLangChain()

    prompt = """Your role is to provide the customer's perspective of the conversation.
                Summarize this for the representative.\
                Describe how the customer might feel.\
                Describe how the customer might view the problem.\
                
                Limit your response to 2 sentences.
                
                Customer perspective:
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{complaint}"),
        ]
    )
    # chain = template | client.client_completion

    chain = (RunnablePassthrough.assign(
        context=get_historical_info_context_chain()
    )
             | template
             | client.client_completion
             )

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
    chain = template | client.client_completion
    return chain


class mAgentCustomer:
    def get_historical_context_chain(self):
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        contextualize_q_chain = contextualize_q_prompt | llmchat | StrOutputParser()
        return contextualize_q_chain

    def get_uncivil_chain(self):
        qa_info_prompt = """
            Your role is to act like a CUSTOMER seeking support. \
            The user is a support representative. \
            Respond to the question as if you were the customer. \
            Do NOT reveal your role.\
            
            If the user is asking for a specific detail, respond with a believable answer.\
            If customer has agreed with response then respond with "FINISH:999"
            After 7-10 turns, respond with messages to close the conversation.\
            After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            
            Phrase your responses like an UNCIVIL customer:\
            - Talk in a rude, impolite, and disrespectuful tone of voice.\
            - Do NOT use good manners. Do NOT use courtesy.\
            - Act with disregard to others.\
            
            
            Representative: {question}
            Customer:
        """
        qa_info = ChatPromptTemplate.from_messages(
            [
                ("system", qa_info_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", '''
                    Representative asked: {question}
                '''),
            ]
        )
        rag_chain_info = (
                RunnablePassthrough.assign(
                    context=self.history_chain
                )
                | qa_info
                | llmchat
        )
        return rag_chain_info

    def invoke(self, user_input):
        ai_msg = self.uncivil_chain.invoke({"chat_history": user_input['chat_history'], "question": user_input['input']})

        return ai_msg.content

    def __init__(self):
            self.history_chain = self.get_historical_context_chain()
            self.uncivil_chain = self.get_uncivil_chain()
#%%
