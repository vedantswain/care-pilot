import os

#import pandas as pd

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


#JOYYYYYYYY Load the service quality reviews dataset
#dataset_path = '/Users/max/Desktop/GitHub/pro-pilot/Service_Quality_reviews.csv'
#reviews_df = pd.read_csv(dataset_path)
#service_quality_df = reviews_df[reviews_df['Category'] == 'Service Quality']
#complaints = service_quality_df['Text'].tolist()


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

        # ### However, not always start with a rhetorical question that copied from representative's response ###
        # ### Be more creative and sounds like human-being. 
   
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{complaint}"),
        ]
    )
    contextualize_q_chain = contextualize_q_prompt | llmchat | StrOutputParser()
    return contextualize_q_chain

# def agent_coworker_info():
#     client = mLangChain()
#     prompt = """Your role is to help a service representative by providing INFORMATIONAL SUPPORT. \
#                 The representative is chatting online with a customer complaining about {product}.  \
                
#                 Given the chat history,
#                 provide 2-3 hints to help the representative's response.\
#                 The hints should direct the representative to do ONLY ONE of the following:\
                
#                 1) Inquire more details about the problem. OR \
#                 2) Request the customer to troubleshoot. OR \
#                 3) Provide a solution to resolve the customer's need. \
                
#                 Each cue should be a single phrase of less than 10 words.\
#                 Do NOT number the cues.\
                
#                 Customer message: {complaint}
#                 Hints: 
#             """
#     template = ChatPromptTemplate.from_messages(
#         [
#             ("system", prompt),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{product}: {complaint}"),
#         ]
#     )
#     chain = template | client.client_completion

#     chain = (RunnablePassthrough.assign(
#         context=get_historical_info_context_chain()
#     )
#              | template
#              | llminfo
#              )
    
#     def extract_cues(chain_output):
#         cues_text = chain_output.content
#         # Assuming each cue is separated by a newline in the chain_output.
#         cues = cues_text.split('\n')
#         # Filter out any empty strings or whitespace-only strings
#         cues = [cue.strip() for cue in cues if cue.strip()]
#         # Return the first 2 - 3 cues
#         processed_cues = [re.sub(r'^\d+\.\s*', '', cue) for cue in cues]
#         return processed_cues[:3]
    
#     chain = chain | extract_cues

#     return chain

# middle///
class mAgentInfo:
    def __init__(self):
        self.info_chain = self.agent_coworker_info()

    def invoke(self, user_input):
        info_cue = self.info_chain.invoke({'product':user_input['product'], 'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})

        return info_cue
    
    def get_historical_info_context_chain(self):
        contextualize_q_system_prompt = """Given a chat history and the latest user input \
            which might reference context in the chat history, formulate a standalone statement \
            which can be understood without the chat history. Do NOT respond to the statement, \
            just reformulate it if needed and otherwise return it as is."""
        
            ### However, not always start with a rhetorical question that copied from representative's response ###
            ### Be more creative and sounds like human-being.
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{complaint}"),
            ]
        )
        contextualize_q_chain = contextualize_q_prompt | llmchat | StrOutputParser()
        return contextualize_q_chain
    
# Mid panel - cues
    def agent_coworker_info(self):
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
        # #           INFORMATIONAL SUPPORT point to the solution to the FIVE categories of complaints: 
        #             <Service Quality>, <Product Issue> < Pricing and Charges> <Policy> <Resolution> 
        #             The representative is chatting online with a grummpy customer complaining about {product}.  \
                    
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


# def agent_coworker_trouble():
#     client = mLangChain()
#     prompt = """Your role is to help a service representative by providing PROCEDURAL SUPPORT. \
#                 The representative is chatting online with a customer complaining about {product}. \
#                 Given the chat history,
#                 list 3-7 steps to guide the representative in resolving the customer complaint.\
#                 Review the similar PROCEDURAL SUPPORT history if exist, then assess the current situation in depth and provide detailed steps for resolution\
#                 if not exist, offer an alternative solution that can solve current solution as detail as possible\

#                 Do NOT include steps that have already been tried.\
#                 Every step should be less than 10 words.\
                
#                 Customer message: {complaint}
#                 Troubleshooting Steps: 
#             """
#     template = ChatPromptTemplate.from_messages(
#         [
#             ("system", prompt),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{product}: {complaint}"),
#         ]
#     )
#     chain = template | client.client_completion

#     chain = (RunnablePassthrough.assign(
#         context=get_historical_info_context_chain()
#     )
#              | template
#              | client.client_completion
#              )

#     return chain

# Left Info Panel
class mAgentTrouble:
    def __init__(self):
        self.trouble_chain = self.agent_coworker_trouble()

    def invoke(self, user_input):
        trouble_steps = self.trouble_chain.invoke({'product':user_input['product'], 'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})

        return trouble_steps
    
    def agent_coworker_trouble(self):
        client = mLangChain()
        prompt = """Your role is to help a service representative by providing PROCEDURAL SUPPORT. \
                    The representative is chatting online with a customer complaining about {product}. \
                    Given the chat history,
                    list 3-7 steps to guide the representative in resolving the customer complaint.\
                    Review the similar PROCEDURAL SUPPORT history if exist, then assess the current situation in depth and provide detailed steps for resolution\
                    if not exist, offer an alternative solution that can solve current solution as detail as possible\

                    Do NOT include steps that have already been tried.\
                    Every step should be less than 10 words.\     

                    Customer message: {complaint}
                    Troubleshooting Steps: 
                """
                    #     ###format every step based on the following form: 
                    # Step 1: \
                    # \
                    # step2:\
                    # \
                    # ... ###
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{product}: {complaint}"),
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

# Right Emo Panel-representative's thought
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

# def agent_coworker_emo_perspective():
#     client = mLangChain()

#     prompt = """Your role is to provide the customer's perspective of the conversation.
#                 Summarize this for the representative.\
#                 Describe how the customer might feel.\
#                 Describe how the customer might view the problem.\
                
#                 Limit your response to 2 sentences.
#                 Write sentence using 2nd person pronouns as subject
                
#                 Customer perspective:
#             """
#     template = ChatPromptTemplate.from_messages(
#         [
#             ("system", prompt),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{complaint}"),
#         ]
#     )
#     # chain = template | client.client_completion

#     chain = (RunnablePassthrough.assign(
#         context=get_historical_info_context_chain()
#     )
#              | template
#              | client.client_completion
#              )

#     return chain

# PERSPECTIVE / toughts  + reframing
class mAgentEP:
    def __init__(self):
        self.ep_chain = self.agent_coworker_emo_perspective()
        self.rephrase = self.paraphraseResponse()

    def invoke(self, user_input):
        emo_perspec = self.ep_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        final_res = self.rephrase.invoke({'response': emo_perspec})

        return final_res
    
# shoes
    def agent_coworker_emo_perspective(self):
        client = mLangChain()

# 
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
        chain = template | client.client_completion

        # chain = (RunnablePassthrough.assign(
        #     context=get_historical_info_context_chain()
        # )
        #         | template
        #         | client.client_completion
        #         )

        return chain
    
    ### this something wrong here!!!!! it always rephrase the prompts
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


def agent_sender_fewshot_twitter():
    client = mLangChain()
    prompt = """Your role is to act like a customer seeking support. \
                You are messaging a service representative via the support chat.\
                You ONLY play the role of the customer. Do NOT play the role of the representative. \
                Style your complaint based on your feelings. \
                Initiate the chat with a ONLY ONE complaint message. \
                
                Product: Mobile Network               
                Feeling: You are NOT grateful. You are NOT ranting. You are NOT expressive.\
                Complaint: O2 I received this a few weeks ago, since then I've been getting 2/3 calls a day from a telemarketer. Is someone using your name?\
                
                Product: Air Travel
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: First flight for long time with British Airways. Now over one 1h delay for the short jump FRA-LCY and NO one here to provide status updates\
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are NOT ranting. You are expressive.\
                Complaint: You‚ have paralysed my phone with your update grrrrrrrrrr\
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  After the 11.0.2 my phone just sucks most of the apps are broken, wifi disconnects frequently apple. Painfulupdate! \
                
                Product: Mobile Device
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint:  Apple Support ios11 update - is still killing my battery within 12 hours - phone is 10 months old - it's a disgrace - used to get 2 days \
                
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
                Complaint: hi #apple, I‚ have a concern about the latest ios is too slow on iphone6 and i am not happy with it. Any solution please? \

                Product: Mobile App
                Feeling: You are grateful. You are NOT ranting. You are expressive.\
                Complaint: Please help! Spotify Premium skipping through songs constantly on android tablet  bluetooth speaker. Tried everything! \
                
                Product: Convenience Store                
                Feeling: You are NOT grateful. You are ranting. You are NOT expressive.\
                Complaint: Got id'd Tesco for buying one Adnams Broadside. Is being blind part of the job-spec? I am 35 and 99 kilos. \
                
                Product: {product}
                Feeling: You are {is_grateful}. You are {is_ranting}. You are {is_expression}.\
                Complaint:
            """
                ###your complaints ONLY have FIVE categories below:
                # 1.Service Quality: Issues related to the immediate experience of human-to-human service interactions, such as delays, staff behavior, and communication errors.
                # 2.Product Issues: Concerns related to physical or functional aspects of a product or service, including defects, mismatches between expectation and reality, safety, and accessibility.
                # 3.Pricing and Charges: Financial discrepancies encountered before, during, or after the service, including overcharging, undisclosed fees, or refund problems.
                # 4.Policy: The rules and guidelines set by the company that impact customer experiences, especially when these policies lead to grievances due to perceived unfairness or inflexibility. This category encompasses non-price-related issues that don't fit under other categories but should have a policy in place.
                # 5.Resolution: The actions taken by a company to address and resolve complaints, focusing on the effectiveness and customer satisfaction with the solutions provided. This should mainly include responses made after a complaint has been submitted, and response has been received, where the customer still remains dissatisfied with the resolution.\

                # Ensure diversity in examples to avoid repetition. Use varied scenarios for different contexts instead of repeating the same example, like the air conditioner for hotels.\
                # Implement a mechanism to track used examples and prevent their reuse. Introduce new examples to maintain diversity.\
                # Check for and filter out irrelevant or junk responses like 'I can't assist with this task.' Ensure that initial complaints are relevant and meaningful.\###
   
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
        ]
    )
    chain = template | client.client_completion
    return chain
    
# def limitation_sender_zeroshot():
#     client = mLangChain()
#     prompt = """
#                 Your role is to set up limitations for the customer service representative.\
#                 You are messaging a service representative via the support chat.\

#                 The representatives could be positioned as interns or assistant representatives with restricted powers.\
#                 Here are the specific limitations:
    
#                 1. Representatives cannot offer coupons or discounts over the price of product.
#                 2. Compensation provided cannot exceed $100.
#                 3. Representatives are not authorized to provide immediate services or upgrades without permission from manager.
#                 4. Any compensation or service adjustments above $100 need to be approved by a supervisor.
#                 5. Representatives should follow a standard protocol for escalating issues that cannot be resolved within these limitations.
#                 6. Representatives must document all customer interactions and resolutions offered.

#                 Generate a detailed guideline based on these limitations.

#             """
#     template = ChatPromptTemplate.from_messages(
#         [
#             ("system", prompt),
#         ]
#     )
#     chain = template | client.client_completion
#     return chain

class mAgentER:
    def __init__(self):

        self.situation_chain = self.agent_coworker_emo_situation()
        self.thought_chain = self.agent_coworker_emo_thought()
        self.reframe_chain = self.agent_coworker_emo_reframe()

    def invoke(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history']})
        reframe = self.reframe_chain.invoke({'thought':thought, 'situation':situation})

        return reframe.strip()
    
    def invokeThought(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history']})
        
        return thought.strip()

    def agent_coworker_emo_situation(self):
        client = mLangChain()

# the latest input is the last message from the [user = representative]?

        prompt = """The chat history describes a representative chatting online with a complaining customer. \
                    The latest input is the last message from the customer. \
                    which can be understood without the chat history.\
                    Describe the situation with respect to the customer's behavior towards the representative.\
                    Include the specifics of the complaint while describing the situation.\
                    
                    Do NOT respond to the input, just summarize the situation.\
                    Do NOT speculate.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{complaint}"),
            ]
        )
        chain = template | client.client_completion

        return chain

    def agent_coworker_emo_thought(self):
        client = mLangChain()

        prompt = """You are roleplaying as the representative talking to a complaining customer.\
                    Refer to the chat history between you and the customer and the latest {complaint} from the customer.\
                    What is the representative thinking about the situation?\
                    Be concise. Only 2 sentences.\
                    
                    Situation: An mturk requester rejected my task and I wasn't sure why because I work very hard on my tasks. Being new it affected my approval rating more negatively.\
                    Thought: I'm not smart enough to succeed at mturk\
                    
                    Situation: I asked my daughter a question, and she responded in a snotty way.\
                    Thought: She doesn't love me like she used to.\
                    
                    Situation: I got upset at my boss for not putting me in a temporary promotion to act as supervisor of our team.\
                    Thought: I wasn't valued as much as the other person.\
                    
                    Situation: I had been working on a project at work for a very long time, but a higher up manager contacted my boss and asked about it, insinuating I wasn't delivering it fast enough.\
                    Thought: I'm working on this as fast as I possibly can.\
                    
                    Situation: I tried on my wedding dress in front of my family. My mother was excited and told me I was beautiful, but other members of my family made comments about my weight. I was told to not eat and exercise so I could be beautiful.\
                    Thought: I'm a fat ugly troll.\
                    
                    Situation: I was reprimanded at work for standing up to a coworker who was bullying another co-worker.\
                    Thought: It was unfair that I was the one to get in trouble for defending a weaker person.\
                    
                    Situation: {situation}\
                    Thought:
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{situation}: {complaint}"),
            ]
        )
        chain = template | client.client_completion

        return chain

    def agent_coworker_emo_reframe(self):
        client = mLangChain()

        prompt = """You are a representative chatting online with a complaining customer.\
                    Reframe your thoughts in the given situation.
                    
                    Situation: An mturk requester rejected my task and I wasn't sure why because I work very hard on my tasks. Being new it affected my approval rating more negatively.\
                    Thought: I'm not smart enough to succeed at mturk\
                    Reframe: It seems like there was some miscommunication. It doesn't mean that I do not have the skills to do well with mturk. I should reach out to see if I can get more clarity on why my task was rejected.\
                    
                    Situation: I asked my daughter a question, and she responded in a snotty way.\
                    Thought: She doesn't love me like she used to.\
                    Reframe: Kids say snappy things to their parents all the time. It doesn't mean I'm a bad parent or that she doesn't love me.\
                    
                    Situation: I got upset at my boss for not putting me in a temporary promotion to act as supervisor of our team.\
                    Thought: I wasn't valued as much as the other person.\
                    Reframe: I should ask my boss why I was not selected for the promotion. Maybe the reason will be something other than my work ethic. Maybe my boss will reassure that I am still valuable to the company.\
                    
                    Situation: I had been working on a project at work for a very long time, but a higher up manager contacted my boss and asked about it, insinuating I wasn't delivering it fast enough.\
                    Thought: I'm working on this as fast as I possibly can.\
                    Reframe: I am stressed by trying to compare how fast I am working on this to how fast I think other people complete their assignments. I know I am being efficient with my time and producing good work. I need to focus on that to get this task done.\
                    
                    Situation: I tried on my wedding dress in front of my family. My mother was excited and told me I was beautiful, but other members of my family made comments about my weight. I was told to not eat and exercise so I could be beautiful.\
                    Thought: I'm a fat ugly troll.\
                    Reframe: The commend about my weight hurt and have me feeling self conscious. I'm glad my mother thinks I'm beautiful and know that my weight does not dictate my worth.\
                    
                    Situation: I was reprimanded at work for standing up to a coworker who was bullying another co-worker.\
                    Thought: It was unfair that I was the one to get in trouble for defending a weaker person.\
                    Reframe: I can own some responsibility for this conflict that occurred at work.\
                    
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
    
    def get_civil_chain(self):
        qa_info_prompt = """
            Your role is to act like a CUSTOMER seeking support. \
            The user is a support representative. \
            Respond to the question as if you were the customer. \
            Do NOT reveal your role.\
            
            If the user is asking for a specific detail, respond with a believable answer.\
            If customer has agreed with response then respond with "FINISH:999"
            After 10 - 12 turns, respond with messages to close the conversation.\
            After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            
            Phrase your responses like an CIVIL customer:\
            - Talk in a gentle, polite, and respectuful tone of voice.\
            - Do use good manners. Do use courtesy.\
            - Act with regard to others.\
            
            
            Representative: {question}
            Customer:
        """
        # DO NOT close the conversation when user pose questions and your conversation less than 12 turns.\
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
            The user is a support representative. \
            Respond to the question as if you were the customer. \
            Do NOT reveal your role.\
            
            If the user is asking for a specific detail, respond with a believable answer.\
            If customer has agreed with response then respond with "FINISH:999"
            After 10 - 12 turns, respond with messages to close the conversation.\
            After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            
            Phrase your responses like an UNCIVIL customer:\
            - Talk in a rude, impolite, and disrespectuful tone of voice.\
            - Do NOT use good manners. Do NOT use courtesy.\
            - Act with disregard to others.\
            

            Representative: {question}
            Customer:
        """

            #         Your MUST act like a grumpy CUSTOMER seeking support. \
            # Your audience is a support representative. \
            # Respond to your audience as if you were the customer. \
            # Do NOT reveal your role.\
            # Ensure every turn is one to three sentences, and DO NOT make it too long to read.\
            
            # If the user is asking for a specific detail, respond with a believable answer.\
            # If customer has agreed with response then respond with "FINISH:999"
            # After 10 - 12 turns, respond with messages to close the conversation.\
            # After 12 turns, do NOT respond further, only respond with "FINISH:999".\
            # DO NOT close the conversation when user pose questions.\
            # DO NOT close the conversation when it is less than 12 turns.\

            
            # Phrase your responses like an UNCIVIL customer:\
            # - Use a rude, impolite, and disrespectful tone.
            # - DO NOT show good manners or courtesy.
            # - DO NOT use a polite or nice tone.
            # - Show disregard for others.
            
            # <Your complaints can ONLY fall into one of the following FIVE categories:
            # 1. Service Quality: Issues related to the immediate experience of human-to-human service interactions, such as delays, staff behavior, and communication errors.
            # 2. Product Issues: Concerns related to physical or functional aspects of a product or service, including defects, mismatches between expectation and reality, safety, and accessibility.
            # 3. Pricing and Charges: Financial discrepancies encountered before, during, or after the service, including overcharging, undisclosed fees, or refund problems.
            # 4. Policy: The rules and guidelines set by the company that impact customer experiences, especially when these policies lead to grievances due to perceived unfairness or inflexibility. This category encompasses non-price-related issues that don't fit under other categories but should have a policy in place.
            # 5. Resolution: The actions taken by a company to address and resolve complaints, focusing on the effectiveness and customer satisfaction with the solutions provided. This should mainly include responses made after a complaint has been submitted, and a response has been received, where the customer still remains dissatisfied with the resolution.>

            # Ensure diversity in examples to avoid repetition. 
            # Use diverse examples to prevent repetition. Track used examples to avoid reuse and introduce new scenarios for variety.\
            # Avoid repeating the same example, like the air conditioner for hotels.\
            # Filter out irrelevant or junk responses. Ensure initial complaints are relevant and meaningful.
            
            # Your TASK is to escalate complaints to challenge the representative. As the conversation progresses, increase the intensity of the complaints.
            
            # ###Example Complaint for Training###

            # ```Premium economy don’t waste your money on an overnight flight! 
            # Going out is acceptable but the night flight we had was a disgrace! 
            # The food (I use this term lightly) wasn’t fit for dogs on our flight, 
            # it was salmon we think as it didn’t taste of anything, 
            # a meat of some kind but was too tough to stick a fork into let alone eat it. 
            # The veg tasted burnt, bread roll was ok. (Not really a saving grace). 
            # One cup of tea or coffee at breakfast and don’t bother asking what was in the box left on our table!
            # I didn’t bother trying it. The look on other people’s faces was good enough for me to know don’t bother! 
            # Which in comparison to the outbound flight (London to Orlando) was worlds apart, 
            # greeted with a drink which was the first of many, dinner was nice, the steak edible, 
            # veg cooked just right and dessert was nice with plenty of drinks! 
            # Inflight entertainment was good even though there was supposed to be WiFi but couldn’t log on so saved some money there. 
            # I really thought this was going to be the best way to travel. 
            # Oh a broken seat for one of our party was a bit disappointing, 
            # homeward bound and the inflight entertainment seem rather lacklustre which leads me to think it was an older plane. 
            # But that really shouldn’t happen. What is not told when booking, homeward flight on the top of your ticket if you have TSA PRE you don’t have to join the massive queue, 
            # look for pre entered TSA line that’s the one that’s empty cause they tell no one about it.```
        
            # ### generate complanits like the example above, and step by step

            # 1. Summarize the main issues you are facing, acting as the grumpy CUSTOMER.
            # 2. Breaking Down the Issues to ensure the conversation lasts 10-12 turns.
            # 3. Generating Responses to CHALLENGE the representative based on their responses. ###
        
            # Representative: {question}
            # Customer:
        
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
