from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import langchain_openai as lcai

import os
from dotenv import load_dotenv
ROOT_RELATIVE_PATH = os.path.dirname(os.path.abspath(''))
project_env = os.path.join(ROOT_RELATIVE_PATH, 'project.env')
load_dotenv(project_env)

DEBUG = False

llmemo = lcai.AzureChatOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment="PROPILOT",
    openai_api_version="2024-05-01-preview",
    model_name="gpt-4o",
    temperature=1,
)

class mAgentER_validation:
    def __init__(self):
        self.situation_chain = self.agent_coworker_emo_situation()
        self.thought_chain = self.agent_coworker_emo_thought()
        self.reframe_chain = self.agent_coworker_emo_reframe()

    def invoke(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history']})
        reframe = self.reframe_chain.invoke({'thought':thought, 'situation':situation})


        rephrase_thought = self.rephrase().invoke({'thought':thought})
        rephrase_reframe = self.rephrase_rf().invoke({'reframe_thought':reframe})

        if DEBUG:
            print(f"{thought}\n -> \n{rephrase_thought}\n")
            print()
            print(f"{reframe}\n -> \n{rephrase_reframe}\n")

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
                Rephrase the {reframe_thought} as if you are instructing the representative to think that way.\
                
                The rephrase should be addressed back to the person who has the thought,\
                who should be referred to as "you".\
                Retain all the specific details of the thought.\
                The reader should be able to understand your rephrase without any knowledge of the original thought.\
                
                Your response should be styled like a message from a supportive coworker.\
                
                The response should be concise and only 2-3 sentences.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{reframe_thought}"),
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


class nAgentER_ctx_pers:
    def __init__(self):
        self.situation_chain = self.agent_coworker_emo_situation()
        self.thought_chain = self.agent_coworker_emo_thought()
        self.reframe_chain = self.agent_coworker_emo_reframe()

    def invoke(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history'],  "personality": user_input['personality']})
        reframe = self.reframe_chain.invoke({'thought':thought, 'situation':situation,  "personality": user_input['personality']})


        rephrase_thought = self.rephrase().invoke({'thought':thought})
        rephrase_reframe = self.rephrase_rf().invoke({'reframe_thought':reframe})

        if DEBUG:
            print(f"{thought}\n -> \n{rephrase_thought}\n")
            print()
            print(f"{reframe}\n -> \n{rephrase_reframe}\n")

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
                Rephrase the {reframe_thought} as if you are instructing the representative to think that way.\
                                
                The rephrase should be addressed back to the person who has the thought,\
                who should be referred to as "you".\
                Retain all the specific details of the thought.\
                The reader should be able to understand your rephrase without any knowledge of the original thought.\
                
                Your response should be styled like a message from a supportive coworker.\
                
                The response should be concise and only 2-3 sentences.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "thought: {reframe_thought}"),
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
            
            
            Keep in mind your {personality}.\
            Ensure that your reframe will be suitable for someone of your predispositions to act on.\
            
                
            Situation: {situation}\
            Thought: {thought}\
            Reframe:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{situation} +  {personality}: {thought}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain

    def agent_coworker_emo_thought(self):

        prompt = """
            Your role is to derive what negative thought a representative might have when faced with the given {situation}.\
            
            You know the representative's {personality}.
            They are predisposed to think in a certain way.\
            
            Situation: {situation}\
            Thought:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{situation} + {personality}: {complaint}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain



class nAgentER_ctx_behv:
    def __init__(self):
        self.situation_chain = self.agent_coworker_emo_situation()
        self.thought_chain = self.agent_coworker_emo_thought()
        self.reframe_chain = self.agent_coworker_emo_reframe()

    def invoke(self, user_input):
        situation = self.situation_chain.invoke({'complaint':user_input['complaint'], 'chat_history':user_input['chat_history']})
        thought = self.thought_chain.invoke({'complaint':user_input['complaint'], 'situation':situation, 'chat_history':user_input['chat_history'],  "behavior": user_input['behavior']})
        reframe = self.reframe_chain.invoke({'thought':thought, 'situation':situation,  "behavior": user_input['behavior']})


        rephrase_thought = self.rephrase().invoke({'thought':thought})
        rephrase_reframe = self.rephrase_rf().invoke({'reframe_thought':reframe})

        if DEBUG:
            print(f"{thought}\n -> \n{rephrase_thought}\n")
            print()
            print(f"{reframe}\n -> \n{rephrase_reframe}\n")

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
                Rephrase the {reframe_thought} as if you are instructing the representative to think that way.\
                                
                The rephrase should be addressed back to the person who has the thought,\
                who should be referred to as "you".\
                Retain all the specific details of the thought.\
                The reader should be able to understand your rephrase without any knowledge of the original thought.\
                
                Your response should be styled like a message from a supportive coworker.\
                
                The response should be concise and only 2-3 sentences.\
                """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "thought: {reframe_thought}"),
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
            
            
            Keep in mind the situation is occuring in the following context: {behavior}.\
            Ensure that your reframe will be suitable for someone who is in that context.\
            
                
            Situation: {situation}\
            Thought: {thought}\
            Reframe:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("user", "{situation} +  {behavior}: {thought}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain

    def agent_coworker_emo_thought(self):

        prompt = """
            Your role is to derive what negative thought a representative might have when faced with the given {situation}.\
            
            The situation occurs in the following context: {behavior}.
            The context helps explain the representative's perception towards their work.\
            
            Situation: {situation}\
            Thought:\
        """
        template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{situation} + {behavior}: {complaint}"),
            ]
        )
        chain = template | llmemo | StrOutputParser()

        return chain