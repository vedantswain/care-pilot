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

class mOpenAI:
    """
    Already setup key and endpoint as environmental variables through bash.
    These can be found on Azure. Currently testing instance `vds-openai-test-001`.
    """
    def __init__(self):
        self.client = oai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = 'TEST'  # This will correspond to the custom name you chose for your deployment when you deployed a model. Use a gpt-35-turbo-instruct deployment.

    def demo(self, start_phrase='Write a tagline for an ice cream shop for orcs.', token_lim=15):
        # Send a completion call to generate an answer
        print('Sending a test completion job')
        response = self.client.completions.create(model=self.deployment_name, prompt=start_phrase, max_tokens=token_lim)
        print(start_phrase + response.choices[0].text)

class mLangChain:
    def __init__(self,mlimit=100):
        self.client_prompt = lcai.AzureOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name="TEST",
            model_name="gpt-3.5-turbo-instruct",
        )
        # self.client_agent = lcai.AzureChatOpenAI(
        #     openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        #     azure_deployment="TEST-Chat-0613",
        #     openai_api_version="2023-12-01-preview",
        #     model_name="gpt-3.5-turbo",
        # )
        self.client_agent = lcai.AzureChatOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment="NUHAI-GPT4",
            openai_api_version="2024-02-15-preview",
            model_name="gpt-4",
        )
        self.embeddings = lcai.AzureOpenAIEmbeddings(
            openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
            openai_api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment="TEST-Embedding",
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Your vocabulary is limited to a 5 year old american."),
            ("user", "{input}")
        ])
        self.prompt_limit = mlimit

    def set_prompt_limit(self, limit):
        self.prompt_limit = limit

    def set_prompt(self, system, user):
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", user)
        ])

    def set_context(self, docs):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.documents = self.text_splitter.split_documents(docs)
        self.vector = FAISS.from_documents(self.documents, self.embeddings)
        self.document_chain = create_stuff_documents_chain(self.client_prompt, self.prompt_template)
        self.retriever = self.vector.as_retriever()
        self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)

    def set_chain_history(self):
        self.contextualize_history_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        self.contextualize_history_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.contextualize_history_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )
        self.history_chain = self.contextualize_history_prompt | self.client_prompt


    def set_agent(self, name="<tool>", description="<desc>", system='You are a helpful assistant', input='{input}'):
        tool = create_retriever_tool(
            self.retriever,
            name,
            description,
        )

        self.tools = [tool]
        self.agent_template = ChatPromptTemplate.from_messages(
                [
                    ("system", system),
                    # MessagesPlaceholder("chat_history", optional=True),
                    ("human", input),
                    MessagesPlaceholder("agent_scratchpad"),
                ]
            )

    def demo(self, start_phrase='Write a tagline for an ice cream shop for orcs.', token_lim=15):
        # Send a completion call to generate an answer
        print('Sending a test completion job')
        # response = self.client(start_phrase)
        response = self.client_prompt.invoke(start_phrase)

        print(start_phrase + response)

    def demo_chain(self, start_phrase=None):
        chain = self.prompt_template | self.client_prompt
        response = chain.invoke({"input": start_phrase})

        print(start_phrase + response)

    def demo_chain_context(self, start_phrase=None):
        response = self.retrieval_chain.invoke({"input": start_phrase})
        print(start_phrase + response["answer"])


    def demo_chain_history(self,start_phrase=None):
        response = self.history_chain.invoke(
            {
                "chat_history": [
                    HumanMessage(content="What is Three Kings on Reddit?"),
                    AIMessage(content="""
                    Three Kings on Reddit is a ritual that involves setting up a room with specific items and sitting in a specific position at 3:30 AM. 
                    It is said to allow access to a place called the 'Shadowside', but it is important to follow all instructions and be mentally and spiritually stable before attempting it.
                    """),
                ],
                "input": start_phrase,
            }
        )
        print(start_phrase + response["answer"])

    def demo_rag(self):
        rag_chain = (
                RunnablePassthrough.assign(
                    context=self.history_chain | self.retriever
                )
                | self.prompt_template
                | self.client_prompt
        )

        chat_history = []
        turn = 0
        print("Ask questions about Three Kings:")
        while(True):
            start_phrase=input("User: ")
            if start_phrase=="exit":
                print("System: OK, bye.")
                break
            if turn==self.prompt_limit:
                print("System: Reached local prompt limit, Bye.")
                break
            ai_msg = rag_chain.invoke({"input": start_phrase, "chat_history": chat_history})
            print(ai_msg)
            chat_history.extend([HumanMessage(content=start_phrase), AIMessage(content=ai_msg)])
            turn = turn + 1
            print()

    def demo_agent(self, init_phrase="Hi, I am an agent who can help you understand Three Kings:"):
        self.agent = create_openai_tools_agent(self.client_agent, self.tools, self.agent_template)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

        turn = 0
        chat_history = []
        print(init_phrase)
        while(True):
            start_phrase = input("User: ")
            if start_phrase=="exit":
                print("System: OK, bye.")
                break
            if turn==self.prompt_limit:
                print("System: Reached local prompt limit, Bye.")
                break
            result = self.agent_executor.invoke({"input": start_phrase, "chat_history": chat_history})
            print(result["output"])
            chat_history.extend([HumanMessage(content=start_phrase), AIMessage(content=result["output"])])
            turn = turn + 1
