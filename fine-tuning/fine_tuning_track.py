# Track training status
from openai import AzureOpenAI
from IPython.display import clear_output
import time, os

start_time = time.time()


client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_KEY"),
  api_version="2023-12-01-preview",  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
  azure_deployment="TEST-Chat-0613"
)


# Get the status of our fine-tuning job.
response = client.fine_tuning.jobs.retrieve(job_id)

status = response.status

# If the job isn't done yet, poll it every 10 seconds.
while status not in ["succeeded", "failed"]:
    time.sleep(10)

    response = client.fine_tuning.jobs.retrieve(job_id)
    print(response.model_dump_json(indent=2))
    print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                       int((time.time() - start_time) % 60)))
    status = response.status
    print(f'Status: {status}')
    clear_output(wait=True)

print(f'Fine-tuning job {job_id} finished with status: {status}')

# List all fine-tuning jobs for this resource.
print('Checking other fine-tune jobs for this resource.')
response = client.fine_tuning.jobs.list()
print(f'Found {len(response.data)} fine-tune jobs.')
