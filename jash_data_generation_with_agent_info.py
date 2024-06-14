from dotenv import load_dotenv
import pandas as pd
import os
import openai as oai
import langchain_openai as lcai
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv("project.env")

# Category definitions
categories = {
    "Service Quality": "Issues related to the immediate experience of human-to-human service interactions, such as delays, staff behavior, and communication errors.",
    "Product Issues": "Concerns related to physical or functional aspects of a product or service, including defects, mismatches between expectation and reality, safety, and accessibility.",
    "Pricing and Charges": "Financial discrepancies encountered before, during, or after the service, including overcharging, undisclosed fees, or refund problems.",
    "Policy": "The rules and guidelines set by the company that impact customer experiences, especially when these policies lead to grievances due to perceived unfairness or inflexibility. This category encompasses non-price-related issues that don't fit under other categories but should have a policy in place.",
    "Resolution": "The actions taken by a company to address and resolve complaints, focusing on the effectiveness and customer satisfaction with the solutions provided. This should mainly include responses made after a complaint has been submitted, and response has been received, where the customer still remains dissatisfied with the resolution."
}

# Example prompts for initial complaints
initial_complaint_examples = {
    "Service Quality": [
        "tried to pay a bill for 60 days No service rude CS and several transfers Look up my equipment and give me an acct",
        "itd be nice if the book I waited 4 months for wasnt damaged inside of an undented box",
        "my driver just drove me to the department of air travel instead of the airport rufkm"
    ],
    "Product Issues": [
        "yall lie about your great connection 5 bars LTE still wont load something Smh",
        "whenever I contact customer support they tell me I have shortcode enabled on my account but I have never in the 4 years Ive tried",
        "The change flight search option on your website is broken once again"
    ],
    "Pricing and Charges": [
        "i booked my flight using delta amex card Checking in now amp was being charged for baggage",
        "Im sorry what Its going to COST me 50 to transfer 4000 AA Advantage points to my spouse AmericanAir this is ridiculous",
        "Why am I still receiving a bill for oct when I disconnected by account on sept 20th pls advise amp reverse the charges"
    ],
    "Policy": [
        "y do they charge you for a meat bag at colliers woods branch If you buy meat you r required to supply customers a free bag Poor service",
        "i am a college student why cant i still use my Momsfamily account while Im away at college",
        "Im a  customer getting the runaround from  to unlock ported phones Now my kids dont have phones 2nite Help"
    ],
    "Resolution": [
        "what option do I have if I bought something on eBay and wasnt delivered and eBay closed my claim to get the money back",
        "My flight from MANLHRBWI for Nov 3 was canceled I was excited to try your Club 787 product Only available flight is now to IAD which is a hassle but rebooked anywaymy only option Any availability in first class on BA293 for the troubles please",
        "why wasnt earlier flight offered when I tried to rebook not cool at all Just happened to look at moniter after deplaning"
    ]
}

# Define traits from the table
agent_traits = {
    "C0": "You are a routine-oriented customer support agent who has high conscientiousness and sleep quality, and low openness and cognitive ability.",
    "C1": "You are an emotionally-stable and innovative customer support agent who has high cognitive ability and low neuroticism.",
    "C2": "You are a withdrawn and prone to stress and irritability customer support agent who has low extraversion, agreeableness, conscientiousness, positive affect, sleep quality, and high neuroticism, cognitive ability, negative affect, and anxiety.",
    "C3": "You are a positive, friendly, and well-balanced customer support agent who has high extraversion, agreeableness, conscientiousness, positive affect, sleep quality, and low neuroticism, negative affect, and anxiety.",
    "C4": "You are a curious and adventurous customer support agent who has high openness."
}

# Define prompts
initial_complaint_prompt = """
Generate a realistic initial complaint from a customer in a {domain} setting. The complaint should fit into this category: {category_definition}. Ensure the complaint is concise and limited to 2 sentences, containing all relevant information.
"""

support_agent_prompt = """
You are a customer support agent responding to the customer's complaint: {initial_complaint}. Ensure the response follows company protocol, is concise, and limited to 2 sentences, containing all relevant information.
"""

coworker_reframe_prompt = """
You are a coworker providing emotional support to a customer support agent who has {agent_traits}. Reframe the agent's response to better address the customer's concerns and improve the overall communication: {agent_response}. Ensure the reframe is concise, supportive, and limited to 2 sentences, containing all relevant information.
"""

follow_up_prompt = """
The customer has received a response from the support agent. Generate a follow-up complaint or question from the customer: {support_agent_response}. Ensure the follow-up complaint is concise and limited to 2 sentences, containing all relevant information.
"""

final_response_prompt = """
You are a customer support agent responding to the customer's follow-up complaint or question: {follow_up_complaint}. Ensure the response follows company protocol, is concise, and limited to 2 sentences, containing all relevant information.
"""

qa_uncivil_prompt = """
Given a history of messages, where the AI is a customer and the representative, rephrase the response to the representative's message to sound UNCIVIL. Do NOT reply to the question, ONLY rephrase. This is what UNCIVIL customers do:
- Address others in an unprofessional, disrespectful way—for example, talking down, using degrading remarks or tone of voice.
- Pay little or no attention to others’ opinions.
- Use intimidating or threatening verbal communication—yelling, repeated emotional outbursts, threats, berating or harsh tone of voice, repeatedly interrupting.
- Blaming others for things out of their control.
- Accusing others of incompetence or dismissing their expertise. Ensure the response is concise and limited to 2 sentences, containing all relevant information.
"""

# Create templates
initial_complaint_template = ChatPromptTemplate.from_messages(
    [("system", initial_complaint_prompt)]
)

support_agent_template = ChatPromptTemplate.from_messages(
    [("system", support_agent_prompt)]
)

coworker_reframe_template = ChatPromptTemplate.from_messages(
    [("system", coworker_reframe_prompt)]
)

follow_up_template = ChatPromptTemplate.from_messages(
    [("system", follow_up_prompt)]
)

final_response_template = ChatPromptTemplate.from_messages(
    [("system", final_response_prompt)]
)

uncivil_template = ChatPromptTemplate.from_messages(
    [
        ("system", qa_uncivil_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", '''
            Representative asked: {question}
            Customer responded: {input}
        ''')
    ]
)

# Helper function to generate a message using prompt and model
def generate_message(prompt, variables):
    # Reinitialize the API call
    llmchat = lcai.AzureChatOpenAI(
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="NUHAI-GPT4",
        openai_api_version="2024-02-15-preview",
        model_name="gpt-4",
    )
    chain = LLMChain(prompt=prompt, llm=llmchat)
    response = chain.invoke(variables)
    return response['text']

# Function to validate and retry message generation if necessary
def validate_and_generate(prompt, variables, invalid_responses):
    response = generate_message(prompt, variables)
    while response in invalid_responses or not is_valid_initial_complaint(response):
        response = generate_message(prompt, variables)
    return response

# Function to check if the initial complaint is valid
def is_valid_initial_complaint(complaint):
    invalid_phrases = [
        "I'm sorry, but I can't fulfill this request.",
        "I can't assist with that request.",
        "I'm unable to fulfill this request.",
        "I can't fulfill this request.",
        "I'm not going to rephrase the response as you requested."
    ]
    return not any(phrase in complaint for phrase in invalid_phrases)

# Function to generate 15 scenarios with agent traits
def generate_15_scenarios_with_traits(agent_traits):
    scenarios = []
    invalid_responses = [
        "Sorry, I can't fulfill this request.",
        "I'm sorry, but I can't fulfill this request.",
        "Sorry, but I can't fulfill this request."
    ]
    
    iteration = 1
    for trait_key, trait_description in agent_traits.items():
        for _ in range(3):
            print(f"Generating scenario {iteration} for trait {trait_key}")
            iteration += 1
            
            # Randomly select domain and category for each scenario
            domain = "random"
            category = "random"
            category_definition = "Random complaint"

            # Generate initial complaint
            initial_complaint = validate_and_generate(initial_complaint_template, {
                'domain': domain,
                'category_definition': category_definition
            }, invalid_responses)
            
            # Rephrase initial complaint to be uncivil
            uncivil_initial_complaint = validate_and_generate(uncivil_template, {
                'chat_history': [],
                'question': "What is your complaint?",
                'input': initial_complaint
            }, invalid_responses)
            
            # Generate support agent response
            support_agent_response = validate_and_generate(support_agent_template, {
                'initial_complaint': uncivil_initial_complaint
            }, invalid_responses)

            # Generate coworker reframe for initial response
            coworker_reframe_1 = validate_and_generate(coworker_reframe_template, {
                'agent_traits': trait_description,
                'agent_response': support_agent_response
            }, invalid_responses)

            # Generate follow-up complaint
            follow_up_complaint = validate_and_generate(follow_up_template, {
                'support_agent_response': support_agent_response
            }, invalid_responses)

            # Rephrase follow-up complaint to be uncivil
            uncivil_follow_up_complaint = validate_and_generate(uncivil_template, {
                'chat_history': [],
                'question': support_agent_response,
                'input': follow_up_complaint
            }, invalid_responses)

            # Generate final response from support agent
            final_response = validate_and_generate(final_response_template, {
                'follow_up_complaint': uncivil_follow_up_complaint
            }, invalid_responses)

            # Generate coworker reframe for final response
            coworker_reframe_2 = validate_and_generate(coworker_reframe_template, {
                'agent_traits': trait_description,
                'agent_response': final_response
            }, invalid_responses)

            # Store scenario
            scenarios.append({
                "Trait": trait_key,
                "Initial Complaint": uncivil_initial_complaint,
                "Support Agent Response 1": support_agent_response,
                "Coworker Reframe 1": coworker_reframe_1,
                "Follow-up Complaint": uncivil_follow_up_complaint,
                "Support Agent Response 2": final_response,
                "Coworker Reframe 2": coworker_reframe_2
            })

    return scenarios

# Generate 15 scenarios with traits
scenarios = generate_15_scenarios_with_traits(agent_traits)

df = pd.DataFrame(scenarios)
df.to_csv("/Users/jashparekh/Desktop/scenarios_with_traits2.csv", index=False)

print("Scenarios with traits saved to scenarios_with_traits.csv")

