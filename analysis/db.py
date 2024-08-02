from pymongo import MongoClient
import pandas as pd
import os

client = MongoClient('localhost', 27017)
db = client['flask_db']

collections = {
    'chat_post_task': db.chat_post_task,
    'chat_history': db.chat_history,
    'chat_client_info': db.chat_client_info,
    'chat_in_task': db.chat_in_task,
    'chat_pre_task': db.chat_pre_task
}

# !!! MAKE SURE you have a file called "csv" on your desktop

desktop_path = '/Users/max/Desktop/csv'
os.makedirs(desktop_path, exist_ok=True)


def fetch_and_format_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

chat_post_task_data = fetch_and_format_data(db.chat_post_task)
csv_file_name = os.path.join(desktop_path, "chat_post_task.csv")
chat_post_task_data.to_csv(csv_file_name, index=False)

chat_history_data = fetch_and_format_data(db.chat_history)
csv_file_name = os.path.join(desktop_path, "chat_history.csv")
chat_history_data.to_csv(csv_file_name, index=False)

chat_client_info_data = fetch_and_format_data(db.chat_client_info)
csv_file_name = os.path.join(desktop_path, "chat_client_info.csv")
chat_client_info_data.to_csv(csv_file_name, index=False)

chat_in_task_data = fetch_and_format_data(db.chat_in_task)
csv_file_name = os.path.join(desktop_path, "chat_in_task.csv")
chat_in_task_data.to_csv(csv_file_name, index=False)

chat_pre_task_data = fetch_and_format_data(db.chat_pre_task)
csv_file_name = os.path.join(desktop_path, "chat_pre_task.csv")
chat_pre_task_data.to_csv(csv_file_name, index=False)