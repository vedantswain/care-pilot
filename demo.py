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
from utils import mOpenAI, mLangChain


def run_openai_demo():
    """
    Vanilla Azure OpenAI API demo
    """
    client_OpenAI = mOpenAI()
    client_OpenAI.demo()

def run_demo_langchain():
    """
    Langchain Azure OpenAI API demo:
    - Distinguishes regular invocation from template based invoke
    """
    client_LC = mLangChain()
    client_LC.demo(start_phrase='Who are the orcs in Lord of the Rings?')
    print()
    client_LC.demo_chain(start_phrase='Who are the orcs in Lord of the Rings?')

def contextualize_prompt(client_LC):
    loader = WebBaseLoader("https://creepypasta.fandom.com/wiki/Three_Kings_Ritual")
    # loader = WebBaseLoader("https://palworld.fandom.com/wiki/Palworld")
    docs = loader.load()
    prompt_custom = """Your vocabulary is limited to a 5 year old american. Answer the following question based only on the provided context:

        <context>
        {context}
        </context>
        """
    client_LC.set_prompt(system=prompt_custom, user="{input}")
    client_LC.set_context(docs)

    return client_LC

def run_demo_langchaincontext():
    """
    Langchain Azure OpenAI API demo:
    - Distinguishes regular invocation from template based invoke
    - First prompt fails
    - Second prompt works with context
    """
    client_LC = mLangChain()
    client_LC.demo_chain(start_phrase='What is Three Kings on Reddit?')

    client_LC = contextualize_prompt(client_LC)
    client_LC.demo_chain_context(start_phrase='What is Three Kings on Reddit?')

def run_demo_langchainhistory():
    """
    Langchain Azure OpenAI API demo:
    - Refactor questions using contextual history
    """
    client_LC = mLangChain()
    client_LC = contextualize_prompt(client_LC)
    client_LC.set_chain_history()
    client_LC.demo_chain_history(start_phrase='What items do I need?')

def run_demo_langchainrag():
    """
    Langchain Azure OpenAI API demo:
    - Answer questions based on context
    - Build history
    - Answer subsequent questions based on history
    """
    client_LC = mLangChain(20)
    client_LC = contextualize_prompt(client_LC)
    client_LC.set_chain_history()
    client_LC.demo_rag()


def run_demo_langchainagent():
    """
    Langchain Azure OpenAI API demo:
    - Agent holds a conversation based on context
    """
    client_LC = mLangChain()
    client_LC = contextualize_prompt(client_LC)
    client_LC.set_agent(
        name="Ritual_Guide",
        description="Agent guides you through a specific ritual on Creepy Pasta",
        system="Your vocabulary is limited to a 5 year old american."
    )
    client_LC.demo_agent()

if __name__ == '__main__':
    # run_openai_demo()
    # run_demo_langchain()
    # run_demo_langchaincontext()
    run_demo_langchainhistory()
    # run_demo_langchainrag()
    # run_demo_langchainagent()

    print()
