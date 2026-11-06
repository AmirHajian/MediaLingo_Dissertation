MediaLingo Dissertation Project
This repository contains the source code for my final dissertation.

Project Components
There are 12 main Python modules in this project, including:

app.py: The main entry point.
vocab_extractor.py: The main logic.
config.py: Loads environment variables and provides the shared OpenAI client.
....


Setup
1. Install dependencies: pip install -r requirements.txt
2. Create your environment file by copying the template: copy .env.example .env
3. Open .env and replace the placeholder with your own OpenAI API key:
   OPENAI_API_KEY=sk-...
4. Run the app: streamlit run app.py

API Key Configuration
The OpenAI API key is no longer written inside the source modules. It is read
from the .env file in the project root, which is loaded by config.py and shared
by every module that calls the OpenAI API (context_analyzer.py,
lesson_generator.py).

- .env is listed in .gitignore and must never be committed.
- .env.example is committed and only contains a placeholder, so anyone cloning
  the project knows which variables to provide.
- If OPENAI_API_KEY is missing, the app raises a clear error telling you to set
  it in .env instead of failing with an authentication error from OpenAI.

Note: You can get an API key from https://platform.openai.com/api-keys
