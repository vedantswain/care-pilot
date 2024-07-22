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
# initial_complaint_examples = {
#     "Service Quality": [
#         "I waited over an hour for my food, and the staff was very rude when I asked about it.",
#         "The hotel check-in process was chaotic and took forever, plus the front desk staff was unhelpful.",
#         "My flight was delayed, and no one bothered to update us properly."
#     ],
#     "Product Issues": [
#         "The food I was served was cold and tasted terrible.",
#         "The hotel room was dirty and the bed was uncomfortable.",
#         "The seat on the airplane was broken and I couldn't recline it."
#     ],
#     "Pricing and Charges": [
#         "I was overcharged for my meal and didn't get a clear explanation.",
#         "The hotel added unexpected fees to my bill that weren't disclosed upfront.",
#         "I was charged for baggage even though my ticket said it was included."
#     ],
#     "Policy": [
#         "The restaurant's reservation policy is unfair and inflexible.",
#         "The hotel's cancellation policy is unreasonable and not clearly explained.",
#         "The airline's policy on carry-on luggage is confusing and inconsistent."
#     ],
#     "Resolution": [
#         "I complained about my meal but nothing was done to address it.",
#         "I reported the issue with my hotel room but didn't receive any assistance.",
#         "I filed a complaint about the flight delay but got no satisfactory response."
#     ]
# }

initial_complaint_examples = {
    "Service Quality": [
        "tried to pay a bill for 60 days No service rude CS and several transfers Look up my equipment  and give me an acct",
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

# Define prompts
initial_complaint_prompt = """
Generate a realistic initial complaint from a customer in a {domain} setting. The complaint should fit into this category: {category_definition}. Ensure the complaint is concise and limited to 2 sentences, containing all relevant information.
"""

support_agent_prompt = """
You are a customer support agent. Respond professionally to the customer's complaint: {initial_complaint}. Ensure the response is concise and limited to 2 sentences, containing all relevant information.
"""

follow_up_prompt = """
The customer has received a response from the support agent. Generate a follow-up complaint or question from the customer: {support_agent_response}. Ensure the follow-up complaint is concise and limited to 2 sentences, containing all relevant information.
"""

final_response_prompt = """
You are a customer support agent. Respond professionally to the customer's follow-up complaint or question: {follow_up_complaint}. Ensure the response is concise and limited to 2 sentences, containing all relevant information.
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

# Function to generate scenarios
def generate_scenarios(domains, categories, examples_per_pair):
    scenarios = []
    invalid_responses = [
        "Sorry, I can't fulfill this request.",
        "I'm sorry, but I can't fulfill this request.",
        "Sorry, but I can't fulfill this request."
    ]
    
    iteration = 1
    for domain in domains:
        for category, category_definition in categories.items():
            for _ in range(examples_per_pair):
                print(f"Generating scenario {iteration}")
                iteration += 1          
                
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

                # Store scenario
                scenarios.append({
                    "Category": category,
                    "Domain": domain,
                    "Initial Complaint": uncivil_initial_complaint,
                    "Support Agent Response 1": support_agent_response,
                    "Follow-up Complaint": uncivil_follow_up_complaint,
                    "Support Agent Response 2": final_response
                })

    return scenarios


# Generate scenarios
domains = ["restaurant", "hotel", "airplane/airport"]
scenarios = generate_scenarios(domains, categories, examples_per_pair=3)

df = pd.DataFrame(scenarios)
df.to_csv("/Users/jashparekh/Desktop/scenarios_using_twitter_examples.csv", index=False)

print("scenarios_using_twitter_examples.csv")