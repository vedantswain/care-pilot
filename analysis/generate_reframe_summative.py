import time
import pandas as pd
import agents_validation as av
from langchain_core.messages import AIMessage, HumanMessage

DIR_PATH = '../data'    # Default path is data directory in the project. Already in .gitignore
DIR_SERVER_PATH = DIR_PATH+'server_data/'
DIR_SANITIZED_PATH = DIR_SERVER_PATH+'sanitized_data/'

### Load the data
incidents_df = pd.read_csv(DIR_PATH+'phase1_scenarios.tsv', sep='\t')

defaultPersonalities = {
    "resilient":"They are organized and dependable. They tend to remain composed when facing challenges, but are prone to setting unrealistic expectations.",
    "undercontrolled":"They are outgoing, competitive, and high energy. They tend to work on impulse, but are also prone to frustration.",
    "overcontrolled":"They are detail-oriented and reliable but might appear distant. They tend to work carefully, but are prone to overthinking."
}


defaultBehaviors = {
    "focused":"The conversation takes place about 2 hours into the work shift. The representative has already addressed a few customer complaints before the following incident.",
    "stressed":"The conversation takes place in the second half of the work shift. The representative has been working longer hours over the past few days and has not been taking breaks.",
    "bored":"The conversation takes place at the middle of the work shift. The representative has been spending minimal time on tasks and has been regularly checking their personal messages."
}

def generate_empathetic_msg(incident_row):
    chat_history = [
        AIMessage(content="Client: "+incident_row['Initial Complaint']),
        HumanMessage(content="Representative: "+incident_row['Support Agent Response 1']),
        AIMessage(content="Client: "+incident_row['Follow-up Complaint 1']),
        HumanMessage(content="Representative: "+incident_row['Support Agent Response 2'])
    ]
    reply = incident_row['Follow-up Complaint 2']

    emo_agent = av.mAgentER_validation()
    emo_agent_ctx_pers = av.nAgentER_ctx_pers()
    emo_agent_ctx_behv = av.nAgentER_ctx_behv()

    responses = []
    response_cw_emo = emo_agent.invoke({'complaint':reply, "chat_history": chat_history})
    response_row = {
        "user_id": "system",
        "incident_id": incident_row['Incident ID'],
        "coworker_empathetic_msg": response_cw_emo['reframe']
    }
    responses.append(response_row)
    print(f"Generated empathetic message for incident {incident_row['Incident ID']}")

    for personality in defaultPersonalities:
        response_cw_emo_ctx = emo_agent_ctx_pers.invoke({'complaint':reply, "chat_history": chat_history, "personality": defaultPersonalities[personality]})
        response_row = {
            "user_id": "system",
            "incident_id": incident_row['Incident ID'],
            "coworker_empathetic_msg": response_cw_emo_ctx['reframe'],
            "context_pers": defaultPersonalities[personality]
        }
        responses.append(response_row)
        print(f"Generated empathetic message for incident {incident_row['Incident ID']} with personality {personality}")

    for behavior in defaultBehaviors:
        response_cw_emo_ctx = emo_agent_ctx_behv.invoke({'complaint':reply, "chat_history": chat_history, "behavior": defaultBehaviors[behavior]})
        response_row = {
            "user_id": "system",
            "incident_id": incident_row['Incident ID'],
            "coworker_empathetic_msg": response_cw_emo_ctx['reframe'],
            "context_behv": defaultBehaviors[behavior]
        }
        responses.append(response_row)
        print(f"Generated empathetic message for incident {incident_row['Incident ID']} with behavior {behavior}")

    print()
    return responses

'''
Generate empathetic messages for each incident
Each message takes at max 9 seconds to generate
7 messages for each incident: 1 default, 3 for each personality, 3 for each behavior
Total time to generate messages for 1 incident: 7*9 = 63 seconds
Total time to generate messages for 45 incidents: 45*63 = 2835 seconds = 47.25 minutes
Adding 30 seconds in between each incident for a break
Total time to generate messages for 45 incidents: 45*63 + 44*30 = 2835 + 1320 = 4155 seconds = 69.25 minutes
'''
def generate_empathetic_msgs(incidents_df):
    responses = []
    for index, row in incidents_df.iterrows():
        responses += generate_empathetic_msg(row)
        print("Taking a 30 second break...")
        time.sleep(30)
        print()

    responses_df = pd.DataFrame(responses)
    return responses_df

responses_df = generate_empathetic_msgs(incidents_df)
responses_df.to_csv(DIR_PATH+'phase1_empathetic_msgs.tsv', sep='\t', index=False)