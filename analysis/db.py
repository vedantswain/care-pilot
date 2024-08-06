from pymongo import MongoClient
import pandas as pd
import os, sys

client = MongoClient('localhost', 27017)
db = client['flask_db']

collections = {
    'chat_post_task': db.chat_post_task,
    'chat_history': db.chat_history,
    'chat_client_info': db.chat_client_info,
    'chat_in_task': db.chat_in_task,
    'chat_pre_task': db.chat_pre_task,
    'summative_writing': db.summative_writing
}


def fetch_and_format_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def mongo_to_tsv(collection, file_name):
    data = fetch_and_format_data(collection)
    file_name = os.path.join(DIR_PATH, file_name)
    data.to_csv(file_name, sep='\t', index=False)
    print(f"Data saved to {file_name}")


### If argument provided, it will be used as DIR_PATH
DIR_PATH = '../data'    # Default path is data directory in the project. Already in .gitignore
if len(sys.argv) > 1:
    DIR_PATH = sys.argv[1]
os.makedirs(DIR_PATH, exist_ok=True)


mongo_to_tsv(db.chat_post_task, 'chat_post_task.tsv')
mongo_to_tsv(db.chat_history, 'chat_history.tsv')
mongo_to_tsv(db.chat_client_info, 'chat_client_info.tsv')
mongo_to_tsv(db.chat_in_task, 'chat_in_task.tsv')
mongo_to_tsv(db.chat_pre_task, 'chat_pre_task.tsv')
mongo_to_tsv(db.summative_writing, 'summative_writing.tsv')