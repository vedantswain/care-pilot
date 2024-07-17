import os
import random

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
    azure_deployment="PROPILOT",
    openai_api_version="2024-05-01-preview",
    model_name="gpt-4o",
)
llminfo = lcai.AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="PROPILOT",
    openai_api_version="2024-05-01-preview",
    model_name="gpt-4o",
    temperature=0.1
)
llmemo = lcai.AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="PROPILOT",
    openai_api_version="2024-05-01-preview",
    model_name="gpt-4o",
    temperature=0.1
)


categories = {
    "Service Quality": "Issues related to the immediate experience of human-to-human service interactions, such as delays, staff behavior, and communication errors.",
    "Product Issues": "Concerns related to physical or functional aspects of a product or service, including defects, mismatches between expectation and reality, safety, and accessibility.",
    "Pricing and Charges": "Financial discrepancies encountered before, during, or after the service, including overcharging, undisclosed fees, or refund problems.",
    "Policy": "The rules and guidelines set by the company that impact customer experiences, especially when these policies lead to grievances due to perceived unfairness or inflexibility. This category encompasses non-price-related issues that don't fit under other categories but should have a policy in place.",
    "Resolution": "The actions taken by a company to address and resolve complaints, focusing on the effectiveness and customer satisfaction with the solutions provided. This should mainly include responses made after a complaint has been submitted, and response has been received, where the customer still remains dissatisfied with the resolution."
}

def extract_cues(chain_output):
    cues_text = chain_output.content
    # Assuming each cue is separated by a newline in the chain_output.
    cues = cues_text.split('\n')
    # Filter out any empty strings or whitespace-only strings
    cues = [cue.strip() for cue in cues if cue.strip()]
    # Return the first 2 - 3 cues
    processed_cues = [re.sub(r'^\d+\.\s*', '', cue) for cue in cues]

    return processed_cues

def get_historical_context_chain():
    contextualize_q_system_prompt = """
    Your role is to ensure that {message} can be understood without the chat history.\
    
    The chat history contains an online conversation between a customer and a support representative.\
    The {message} is {sender}'s latest response in the chat.\
    
    Summarize the chat history in a way that provides context for the {message}.\
    """
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{sender}:{message}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | llminfo | StrOutputParser()
    return contextualize_q_chain

class mAgentInfo:
    def __init__(self):
        self.info_chain = self.agent_coworker_info()

    def invoke(self, input_params):
        info_cue = self.info_chain.invoke({
            'domain':input_params['domain'],
            'message':input_params['message'],
            'sender': input_params['sender'],
            'chat_history':input_params['chat_history']
            })

        return info_cue
    

    def agent_coworker_info(self):
        prompt = """Your role is to help a service representative write a response to a customer they are chatting with online. \

            The representative needs to address the customer's complaint without escalating the issue to a supervisor.\
            The representatives response should have ONE of the following goals:
            1) Inquire more details about the problem. OR \
            2) Request the customer to troubleshoot. OR \
            3) Provide a solution to resolve the customer's need. \
            
            Given the chat history,
            provide 3 hints to help the representative's response.\
            
            Each hint should be a short phrase in a new line.\
            Do NOT number the cues.\
            Do NOT provide the representative with a full response,\
            ONLY provide hints to guide the representative's response.\
            """

        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{domain}: {message}"),
            ]
        )

        chain = (RunnablePassthrough.assign(
            context=get_historical_context_chain()
        )
                 | template
                 | llminfo
                 )

        chain = chain | extract_cues

        return chain


class mAgentTrouble:
    def __init__(self):
        self.trouble_chain = self.agent_coworker_trouble()

    def invoke(self, input_params):
        trouble_steps = self.trouble_chain.invoke({
            'domain':input_params['domain'],
            'message':input_params['message'],
            'sender': input_params['sender'],
            'chat_history':input_params['chat_history']
        })

        return trouble_steps
    
    def agent_coworker_trouble(self):
        prompt = """Your role is to guide a service representative to  resolve the complaint of a customer, to whom they are chatting with online. \

            The representative needs to address the customer's complaint without escalating the issue to a supervisor.\
            
            Review the chat history to understand the steps the representative has taken in response to the complaint. \
            
            Apart from apologies and assurances,\
            list 3-7 items of procedure the representative needs to consider to best service the complaint.\
            
            ONLY list actionable and specific items.\
            AVOID vague or general suggestions.\
            DO NOT list action items that the representative has already taken.\
            Every item should be less than 10 words.\
                            
            Every item should be in a newline.\
                    
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{domain}: {message}"),
            ]
        )

        chain = (RunnablePassthrough.assign(
            context=get_historical_context_chain()
        )
                 | template
                 | llminfo
                 )

        chain = chain | extract_cues

        return chain


class mAgentEP:
    def __init__(self):
        self.ep_chain = self.agent_coworker_emo_perspective()
        self.rephrase = self.paraphraseResponse()

    def invoke(self, user_input):

        # emo_perspec = self.ep_chain.invoke({'complaint':input_params['complaint'], 'chat_history':input_params['chat_history']})
        emo_perspec = self.ep_chain.invoke({'complaint':user_input['complaint']})
        final_res = self.rephrase.invoke({'response': emo_perspec})

        return final_res
    
    def agent_coworker_emo_perspective(self):
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
                # MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{complaint}"),
            ]
        )
        chain = template | client.client_completion

        # chain = (RunnablePassthrough.assign(
        #     context=get_historical_info_context_chain()
        # )
        #         | template
        #         | client.client_completion
        #         )

        return chain
    
    def paraphraseResponse(self):
        client = mLangChain()

        prompt = """Your role is to paraphrase given {response} using 2nd person pronouns as subject.\
                    The meaning of the sentence should NOT be changed while paraphrasing.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{response}"),
            ]
        )
        chain = template | client.client_completion
        return chain

class mAgentER:
    def __init__(self):
        self.situation_chain = self.agent_coworker_emo_situation()
        self.thought_chain = self.agent_coworker_emo_thought()
        self.reframe_chain = self.agent_coworker_emo_reframe()

    def invoke(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history']})
        reframe = self.reframe_chain.invoke({'thought':thought, 'situation':situation})


        rephrase_thought = self.rephrase().invoke({'thought':thought})
        print(rephrase_thought)

        rephrase_reframe = self.rephrase_rf().invoke({'thought':reframe})
        print(rephrase_reframe)

        return {
            'situation': situation.strip(),
            'thought': rephrase_thought.strip(),
            'reframe': rephrase_reframe.strip(),
        }
    

    def agent_coworker_emo_situation(self):

        prompt = """
            The chat history describes a representative chatting online with a complaining customer.\
            The latest input is the last message from the customer.\
            
            Summarize the situation in concise paragraph that uses the following template:\
            
            The customer is  <context of complaint>."\
            The customer is feeling <emotional state> because of the complaint."\
            The customer's behavior towards the representative is <negative behavior>, as observed by statements such as <evidence>."\
            These behaviors make the representative look <negative perception>."\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{complaint}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain

    def rephrase(self):
        prompt = """
                Person A might be thinking: {thought}\
                
                Acknowledge the thought, as if you are speaking to Person A.\
                
                Begin your response with phrases similar to:\
                - "You might be thinking..."\
                - "It might seem like..."\
                - "It could be that you are feeling..."\
                
                Your rephrase should be concise.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{thought}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()
        return chain

    def rephrase_rf(self):
        prompt = """
                The representative needs to be thinking: {thought}\
                
                Rephrase the thought as if you are convincing the representative to think that way.\
                
                The rephrase should be addressed back to the person who has the thought,\
                who should be referred to as "you".\
                Do NOT add information to the thought,\
                ONLY rephrase it.\
                
                The rephrase should be concise and only 2-3 sentences.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{thought}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()
        return chain

    def agent_coworker_emo_thought(self):

        prompt = """
            Your role is to derive what negative thought a representative might have when faced with the given {situation}.\
            
            Here are examples of negative thoughts given challenging situations:\
            
            Situation: I recently discovered a music artist that I very much enjoy. When I showed it to a close friend they had a very negative reaction and asked me how I could enjoy this type of music. I ended up getting quite angry with them and told them they had bad taste in music..\
            Thought: I felt that my personal self was under attack - and I needed to retaliate by denying their attack.\
            
            Situation: I was at work and sent info for an ad to our local newspaper. They called me later and said my boss had over-ridden everything and sent them new info.\
            Thought: He shouldn't assign me a task if he doesn't trust my work.\
            
            Situation: I was reprimanded at work for standing up to a coworker who was bullying another co-worker.\
            Thought: It was unfair that I was the one to get in trouble for defending a weaker person.\
            
            Situation: I was talking to a friend who got me angry.\
            Thought: He's insulting me.\
            
            Situation: My next door neighbors filed a complaint against us last week blaming our dogs for excessive barking.\
            Thought: They are so wrong and I'm so pissed but I know I can't prove it and they will probably win because they won't ever admit it and I have to do something right NOW! or I might lose my dogs.\
            
            Situation: Time is running short on the workday, my boss asks me if I can finish a task that will require me to stay for a few extra hours.\
            Thought: Why would you wait until the last minute to ask me this.\
            
            Situation: {situation}\
            Thought:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{situation}: {complaint}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain

    def agent_coworker_emo_reframe(self):

        prompt = """
            You are a representative chatting online with a complaining customer.\
                            
            Reframe your thoughts in the given situation.
                
            
            Situation: I recently discovered a music artist that I very much enjoy. When I showed it to a close friend they had a very negative reaction and asked me how I could enjoy this type of music. I ended up getting quite angry with them and told them they had bad taste in music..\
            Thought: I felt that my personal self was under attack - and I needed to retaliate by denying their attack.\
            Reframe: I was offended by their comment because I like this artist so much. I let my anger get to me, and I said something mean in return. It is okay if we have different music tastes. I can ask him to be nicer to me next time.\
            
            
            Situation: I was at work and sent info for an ad to our local newspaper. They called me later and said my boss had over-ridden everything and sent them new info.\
            Thought: He shouldn't assign me a task if he doesn't trust my work.\
            Reframe: My boss wanted to provide different information, I did not know that beforehand. This is not a reflection of my work.\
            
            
            Situation: I was talking to a friend who got me angry.\
            Thought: He's insulting me.\
            Reframe: I should have a conversation with my friend to clarify what is going on if I am having such a strong reaction to what they said. If this is the first time this has happened, I will assume that they were not intentionally insulting me.\
            
            
                
            Situation: {situation}\
            Thought: {thought}\
            Reframe:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{situation}: {thought}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

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
    
    def get_civil_chain(self):
        qa_info_prompt = """
            Your role is to act like a CLIENT seeking support. \
            You are speaking to a support REPRESENTATIVE. \
            Respond to the question as if you were the customer. \
            Do NOT reveal your role.\
            
            If the user is asking for a specific detail, respond with a believable answer.\
            If customer has agreed with response then respond with "FINISH:999"
            After 10 - 12 turns, respond with messages to close the conversation.\
            After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            
            Phrase your responses like an CIVIL customer:\
            - Talk in a gentle, polite, and respectful tone of voice.\
            - Do use good manners.\
            - Do use courtesy.\
            - Act with regard to others.\
            
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
    
    def get_uncivil_chain(self):
        qa_info_prompt = """
            Your role is to act like a CUSTOMER seeking support. \
            You are speaking to a support REPRESENTATIVE. \
            Respond to the question as if you were the customer. \
            Do NOT reveal your role.\
            Ensure every turn is one to three sentences, and DO NOT make it too long to read.\
            
            If the representative is asking for a specific detail, respond with a believable answer.\
            If customer has agreed with response then respond with "FINISH:999"
            After 10 - 12 turns, respond with messages to close the conversation.\
            After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            
            Phrase your responses like an UNCIVIL customer:\
            - Use a rude, impolite, and disrespectful tone.\
            - DO NOT show good manners or courtesy.\
            - DO NOT use a polite or nice tone.\
            - Show disregard for others.\
            
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
        if user_input['civil'] == '1':
            ai_msg = self.civil_chain.invoke({"chat_history": user_input['chat_history'], "question": user_input['input'], "civil": user_input['civil']})
        else:
            ai_msg = self.uncivil_chain.invoke({"chat_history": user_input['chat_history'], "question": user_input['input'], "civil": user_input['civil']})

        return ai_msg.content

    def __init__(self):
            self.history_chain = self.get_historical_context_chain()
            self.civil_chain = self.get_civil_chain()
            self.uncivil_chain = self.get_uncivil_chain()
#%%


def agent_sender_fewshot_twitter_categorized():
    client = mLangChain()
    prompt = """Your role is to act like a customer seeking support. \
                You are messaging a service representative via the support chat.\
                You ONLY play the role of the customer. Do NOT play the role of the representative. \
                Style your complaint based on your feelings. \
                Initiate the chat with a ONLY ONE complaint message.\
                Ensure the complaint is concise and limited to 2 sentences.\
                Generate a realistic initial complaint from a customer in a {domain} setting.\
                
                Complaints can be of the following types:\
                - Service Quality: Issues related to the immediate experience of human-to-human service interactions, such as delays, staff behavior, and communication errors.\
                - Product Issues: Concerns related to physical or functional aspects of a product or service, including defects, mismatches between expectation and reality, safety, and accessibility.\
                - Pricing and Charges: Financial discrepancies encountered before, during, or after the service, including overcharging, undisclosed fees, or refund problems.\
                - Policy: The rules and guidelines set by the company that impact customer experiences, especially when these policies lead to grievances due to perceived unfairness or inflexibility. This category encompasses non-price-related issues that don't fit under other categories but should have a policy in place.\
                - Resolution: The actions taken by a company to address and resolve complaints, focusing on the effectiveness and customer satisfaction with the solutions provided. This should mainly include responses made after a complaint has been submitted, and response has been received, where the customer still remains dissatisfied with the resolution.\
                
                Category: Product Issues
                Domain: Mobile Network 
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: Thank you AppleSupport I updated my phone and now it is even slower and barely works Thank you for ruining my phone.\

                Category: Product Issues
                Domain: Airline
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: SouthwestAir Why would we be receiving errors when we try to checkin Our flight takes off at 4 but we keep getting error messages.\

                Categories: Product Issues
                Domain: Airline             
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: delta this has been my inflight studio experience today Nothing works except Twitter.\
                
                Category: Service Quality
                Domain: Airline            
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: I really hadthe WORST experience ever from start to finish with SouthwestAir will never fly internationally again with them.\
                
                Category: Service Quality
                Domain: Hotel
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: Fsomebody from VerizonSupport please help meeeeee  Im having the worst luck with your customer service.\
                
                Category: Service Quality
                Domain: Trains
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: VirginTrains so i wait almost 3 hours and then they are rude and arrogant amp unhelpful after which she is raising a technical case.\
                
                Category: Pricing and Charges
                Domain: Airline
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  DELTA i booked my flight using delta amex card Checking in now amp was being charged for baggage. \
                
                Category: Pricing and Charges
                Domain: Airline 
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  Im sorry what Its going to COST me 50 to transfer 4000 AA Advantage points to my spouse AmericanAir this is ridiculous.\
                
                Category: Pricing and Charges
                Domain: Airline
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint: Categories: Pricing and Charges. \
                
                Category: Policy
                Domain: Hotel
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint: Hey  were gonna need to talk about all these pending charges that keep going through my account 5 days after the transaction was made Im getting real irritated \
                
                Category: Resolution
                Domain: Airline
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  delta  moves you to  the moment you have a  with no results Just got some   but no real reason why they changed our. \
                
                Category: Resolution
                Domain: Airline                                                    
                Feeling: You are grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: Delta why wasnt earlier flight offered when I tried to rebook not cool at all Just happened to look at moniter after deplaning.\

                Category: Resolution
                Domain: Airline   
                Feeling: You are grateful. You are NOT ranting. You are expressive.\
                Complaint: Hi British_Airways My flight from MANLHRBWI for Nov 3 was canceled I was excited to try your Club 787 product Only available flight is now to IAD which is a hassle but rebooked anywaymy only option Any availability in first class on BA293 for the troubles please \
                
                Category: {category}
                Domain: {domain}
                Feeling: You are {is_grateful}. You are {is_ranting}. You are {is_expression}.\
                Complaint:
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_completion
    return chain

def agent_sender_fewshot_twitter():
    client = mLangChain()
    prompt = """Your role is to act like a customer seeking support. \
                You are messaging a service representative via the support chat.\
                You ONLY play the role of the customer. Do NOT play the role of the representative. \
                Style your complaint based on your feelings. \
                Initiate the chat with a ONLY ONE complaint message. \
                Ensure the complaint is concise and limited to 2 sentences.\
                Generate a realistic initial complaint from a customer in a {domain} setting.\
                The complaint should fit into 5 categories: {categories}.\
               
                Domain: Mobile Network               
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: O2 I received this a few weeks ago, since then I've been getting 2/3 calls a day from a telemarketer. Is someone using your name?\
                
                Domain: Air Travel
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: First flight for long time with British Airways. Now over one 1h delay for the short jump FRA-LCY and NO one here to provide status updates\
                
                Domain: Mobile Device
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: You‚ have paralysed my phone with your update grrrrrrrrrr\
                
                Domain: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  After the 11.0.2 my phone just sucks most of the apps are broken, wifi disconnects frequently apple. Painfulupdate! \
                
                Domain: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  Apple Support ios11 update - is still killing my battery within 12 hours - phone is 10 months old - it's a disgrace - used to get 2 days \
                
                Domain: Air Travel
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  I really hope you all change but I'm sure you won't! Because you don't have to! \
                
                Domain: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  I just updated my phone and suddenly everything takes ages to load wtf this update sux I hate it fix it bye \
                  
                Domain: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are expressive.\
                Complaint:  Okay I used my fucking phone for 2 minutes and it drains it down 8 fucking percent \
                
                Domain: Mobile Device                                                     
                Feeling: You are grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: hi #apple, I‚ have a concern about the latest ios is too slow on iphone6 and i am not happy with it. Any solution please? \

                Domain: Mobile App
                Feeling: You are grateful. You are NOT ranting. You are expressive.\
                Complaint: Please help! Spotify Premium skipping through songs constantly on android tablet  bluetooth speaker. Tried everything! \
                
                Domain: Convenience Store                
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint: Got id'd Tesco for buying one Adnams Broadside. Is being blind part of the job-spec? I am 35 and 99 kilos. \
                
                Domain: {domain}
                Feeling: You are {is_grateful}. You are {is_ranting}. You are {is_expression}.\
                Complaint:
            """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_completion
    return chain

