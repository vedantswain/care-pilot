# Upload fine-tuning files

import os
from openai import AzureOpenAI
script_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(script_path)

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_KEY"),
  api_version="2024-02-15-preview",  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
)

training_file_name = os.path.join(parent_dir,'training_set.jsonl')
validation_file_name = os.path.join(parent_dir,'validation_set.jsonl')

# Upload the training and validation dataset files to Azure OpenAI with the SDK.

training_response = client.files.create(
    file=open(training_file_name, "rb"), purpose="fine-tune"
)
training_file_id = training_response.id

validation_response = client.files.create(
    file=open(validation_file_name, "rb"), purpose="fine-tune"
)
validation_file_id = validation_response.id

print("Training file ID:", training_file_id)
print("Validation file ID:", validation_file_id)