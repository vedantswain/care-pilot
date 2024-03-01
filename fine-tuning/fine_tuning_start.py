import os
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_KEY"),
  api_version="2023-10-01-preview",  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
  # azure_deployment="CSR"
)

'''
Output after uploading
'''
training_file_id = "file-396de6278d154df8a83fb7420917a414"
validation_file_id =  "file-d50a9ffaaf3b465fa80afda315e9bb0c"

response = client.fine_tuning.jobs.create(
    training_file=training_file_id,
    validation_file=validation_file_id,
    model="gpt-3.5-turbo-0613", # Enter base model name. Note that in Azure OpenAI the model name contains dashes and cannot contain dot/period characters.
)

job_id = response.id

# You can use the job ID to monitor the status of the fine-tuning job.
# The fine-tuning job will take some time to start and complete.

print("Job ID:", response.id)
print("Status:", response.id)
print(response.model_dump_json(indent=2))