import pandas as pd
import re, json

data_rcis_complaints_path = "../data/tagged_selections_by_sentence.csv"
df_complaints = pd.read_csv(data_rcis_complaints_path)
keep_feats = ['MergedSelections', 'Rant', 'Express Emotion', 'Gratitude']

samples = []

def get_rants(rants_only=False,emotion_only=False):
    mask_rant = df_complaints['Rant'] ==  int(rants_only)
    mask_emotion = df_complaints['Express Emotion'] == int(emotion_only)
    print(df_complaints.shape)
    return df_complaints[mask_rant & mask_emotion][keep_feats]

def prep_prompt(x):
    rgx = re.compile('[%s]' % '[]')         ### part of annotation, needs to be removed
    complaint = x["MergedSelections"]
    complaint = rgx.sub('', complaint)

    if bool(x["Rant"])==True:
        add_str_rant = "You are ranting."
    else:
        add_str_rant = "You are NOT ranting."
    if bool(x["Gratitude"])==True:
        add_str_grat = "You are grateful."
    else:
        add_str_grat = "You are NOT grateful."
    if bool(x["Express Emotion"])==True:
        add_str_emo = "You are expressive."
    else:
        add_str_emo = "You are NOT expressive."


    system = {"role": "system", "content": "You are a customer seeking support."+add_str_grat+add_str_rant+add_str_emo}
    assistant = {"role": "assistant","content": complaint}

    sample = {"messages": [system, assistant]}
    samples.append(sample)


TRAIN_COUNT = 8*100
TEST_COUNT = 2*100

df_complaints.sample(frac=1, random_state=42)
df_complaints[keep_feats].apply(prep_prompt, axis=1)
samples_train = samples[:TRAIN_COUNT]
samples_test = samples[-1*TEST_COUNT:]

with open("training_set.jsonl", "w") as jsonl_file:
    for item in samples_train:
        jsonl_file.write(json.dumps(item) + '\n')

with open("validation_set.jsonl", "w") as jsonl_file:
    for item in samples_test:
        jsonl_file.write(json.dumps(item) + '\n')


print(len(samples))