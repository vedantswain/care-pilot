Pro-Pilot
===============================

## Installation
### Virtual Environment Setup
Please setup a virtual environment to run the project:
- Option 1: Create using Python: `python3.x -m venv {your_virtual_env_name}` and activate it: `source {your_virtual_env_name}/bin/activate` (Mac) / `.\venv\Scripts\activate` (Windows)
- Option 2: Use Anaconda: `conda create --name {your_virtual_env_name} python=3.x` and activate it: `conda activate {your_virtual_env_name}`

You can also execute Option 2 using the Anaconda Navigator GUI. `3.x` represents the Python version you want to use. I would recommend using Python 3.11 or higher.

### Module Installation

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

## Getting started
### Accessing Chatbot
- Execute the command `python app.py`. This will start the local server and the application will be accessible at `http://localhost:8080`.
- To interact with the chatbot, open a web browser and enter the URL `http://localhost:8080`. (Chrome Recommanded)
- The chatbot session can be configured using the following URL format: 
    ```
    http://localhost:8080/session_address/?product=YOURPRODUCT&grateful=YOURGRATEFUL&ranting=YOURRANTING&expression=YOUREXPRESSION
    ```
- Replace `YOURPRODUCT` with the specific product name. 
- The parameters `YOURGRATEFUL`, `YOURRANTING`, and `YOUREXPRESSION` accept values `0` or `1`, representing positive and negative sentiments, respectively.

### Managing Data with MongoDB
- Run `mongosh` in your terminal to start MongoDB Shell.
- Connect to the server and select the database associated with the Flask app by running `use flask_db`.
- To view the data within a collection, use the command:
   - `chat_history_collection` — stores chat interaction history.
   - `chat_client_info` — stores user information.
   - `chat_emo_feedback` — stores emotional feedback from users.
    ```
    db.COLLECTION_NAME.find().pretty()
    ```
- If you need to reset a collection, type:
    - This command removes all documents from the specified collection and resets it.
    ```
    db.COLLECTION_NAME.drop()
    ```

## Project Setup
### App.py
#### Features
- Landing Page: Serves as the initial point of interaction where users are greeted.
- Session Management: Generates unique sessions for users to maintain distinct chat histories and interactions.
- Emotional Support: Offers responses based on the emotional content of user interactions.
- Informational Support: Provides factual support based on user queries and chat context.
- Troubleshooting Guide: Delivers step-by-step assistance for resolving user issues.

#### Technical Description
- `/` `hello()` - Entry route that renders the landing page.
- `/chat` `start_chat()` - Creates a new chat session and redirects the user to the chat interface.
- `/<session_id>/` `index(session_id)` - Main chat interface that utilizes the session ID for personalized interactions.
- `/<session_id>/get-reply` `getReply(session_id)` - Handles fetching and sending replies within the chat session.
- `/<session_id>/get-emo-feedback` `getEmoFeedback(session_id)` - Updates the database with user feedback on emotional interactions.
- `/<session_id>/get-emo-support` `getEmoSupport(session_id)` - Provides emotional support responses.
- `/<session_id>/get-info-support` `getInfoSupport(session_id)` - Offers informational support based on the ongoing chat.
- `/<session_id>/get-trouble-support` `getTroubleSupport(session_id)` - Guides users through troubleshooting processes.

### Agents.py
#### Features
- Emotional Support: Captures and processes the emotional context of customer interactions, providing representatives with insight into the customer's emotional state.
- Informational Support: Dynamically retrieves relevant information based on the ongoing conversation to aid representatives in providing factual and detailed responses.
- Procedural Support: Offers step-by-step troubleshooting assistance, guiding representatives through resolving customer issues effectively.
- Historical Context Management: Maintains and utilizes historical conversation context to ensure responses are relevant and personalized.

#### Technical Description
- `agent_coworker_emo()` - Helps service representatives by providing emotional insights into customer complaints.
- `agent_coworker_emo_perspective()` - Provides the customer's perspective in a summarized form to help the representative understand the customer's view and feelings.
- `agent_coworker_info()` - Assists service representatives by providing actionable hints based on the customer's product-related complaints.
- `agent_coworker_trouble()` - Provides procedural support by listing steps to resolve customer complaints.
- `get_historical_info_context_chain()` - Creates a context chain that reformulates statements to be understood without prior chat history.
- `invoke()` - Acts as the primary method to trigger the execution of the defined agent chains based on user input.
