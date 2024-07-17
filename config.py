'''
A single file for string literals that are being used across files.
This ensures that we only need to make changes in one location to reflect it across multiple scripts.
Reduces risk of errors when changing code or introducing new types.
'''
import random

TYPE_EMO_THOUGHT = "You might be thinking"
TYPE_EMO_SHOES = "Put Yourself in the Client's Shoes"
TYPE_EMO_REFRAME = "Be Mindful of Your Emotions"
TYPE_SENTIMENT = "Client's Sentiment"
TYPE_INFO_CUE = "Ways to Continue the Conversation"
TYPE_INFO_GUIDE = "Ways to Help Your Customer"

SUPPORT_TYPE_STRINGS = {
    "TYPE_EMO_THOUGHT" : TYPE_EMO_THOUGHT,
    "TYPE_EMO_SHOES" : TYPE_EMO_SHOES,
    "TYPE_EMO_REFRAME" : TYPE_EMO_REFRAME,
    "TYPE_SENTIMENT" : TYPE_SENTIMENT,
    "TYPE_INFO_CUE" : TYPE_INFO_CUE,
    "TYPE_INFO_GUIDE": TYPE_INFO_GUIDE
}

### Only for testing/debugging
randomQueue = [
    { "id": 1, "name": "Luis H.", "domain": "Airline" , "grateful": 0, "ranting": 0, "expression":0, "civil": 0, "info": 1, "emo": 1},
    { "id": 2, "name": "Jamal K.", "domain": "Hotel", "grateful": 1, "ranting": 0, "expression": 1, "civil": 1, "info": 1, "emo": 0},
    { "id": 3, "name": "Maria N.", "domain": "Airline",  "grateful": 1, "ranting": 1, "expression": 1, "civil": 1, "info": 0, "emo": 1},
    { "id": 4, "name": "Elijah P.", "domain": "Hotel" , "grateful": 0, "ranting": 1, "expression":0, "civil": 0, "info": 0, "emo": 0},
    { "id": 4, "name": "Samantha K.", "domain": "Hotel" , "grateful": 0, "ranting": 1, "expression":0, "civil": 1, "info": 0, "emo": 1}
]

'''
For actual study scenario.
Unlike testing we will keep "grateful": 0, "ranting": 1, "expression":1
Other conditions will maintain fixed order in the queue
'''
studyQueue = [
    { "id": 1, "grateful": 0, "ranting": 1, "expression":1, "civil": 1, "info": 1, "emo": 0},
    { "id": 1, "grateful": 0, "ranting": 1, "expression":1, "civil": 0, "info": 1, "emo": 0},
    { "id": 1, "grateful": 0, "ranting": 1, "expression":1, "civil": 0, "info": 1, "emo": 1},
    { "id": 1, "grateful": 0, "ranting": 1, "expression":1, "civil": 0, "info": 1, "emo": 1},
    { "id": 1, "grateful": 0, "ranting": 1, "expression":1, "civil": 0, "info": 1, "emo": 1}
]

complaintTypes = [
    "Service Quality",
    "Product Issues",
    "Pricing and Charges",
    "Policy",
    "Resolution"
]

def get_study_queue(scenario):
    names = [client['name'] for client  in randomQueue]
    random.shuffle(names)
    random.shuffle(complaintTypes)
    for client_id in range(len(studyQueue)):
        client_name = names[client_id]
        studyQueue[client_id]['name'] = client_name
        studyQueue[client_id]['category'] = complaintTypes[client_id]
        studyQueue[client_id]['domain'] = scenario
        studyQueue[client_id]['avatar'] = "https://avatar.iran.liara.run/username?username="+client_name.replace(' ','+')
    return studyQueue
