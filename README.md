Pro-Pilot
===============================
description

## Installation
Pre-requisite: In order to run the Flask app, please contact admin for access on AZURE_OPENAI_API.

Make sure if Homebrew is installed by running `brew --version`. If not, install Homebrew from [brew.sh](https://brew.sh/).
Navigate to your project directory where `Brewfile` and `requirements.txt` are located and execute the following commands:
```
brew bundle
pip install -r requirements.txt
```

These commands will install all the necessary software and Python packages required for the application. Ensure that Redis and MongoDB are correctly installed by running:
```
redis-cli ping
mongosh --version
```

Start the necessary services using Homebrew:
```
brew services start mongodb-community@7.0
brew services start redis
```

To verify that the services are running, use:
```
brew services list
```

Once your access is approved, Create a `project.env` file in your project directory and add the following environment variables. Replace `YOURSECRETKEYGOESHERE` with your actual secret keys:
```
PYTHONUNBUFFERED=YOURSECRETKEYGOESHERE
AZURE_OPENAI_ENDPOINT=YOURSECRETKEYGOESHERE
AZURE_OPENAI_KEY=YOURSECRETKEYGOESHERE
PLATFORM_OPENAI_KEY=YOURSECRETKEYGOESHERE
AZURE_COSMOS_MONGO_ADMIN=YOURSECRETKEYGOESHERE
AZURE_COSMOS_MONGO_PASS=YOURSECRETKEYGOESHERE
AZURE_COSMOS_MONGO_CONNSTRING=YOURSECRETKEYGOESHERE
```

With all services running and the environment configured, you can start the Flask application by running:
```
python run.py
```

