# config.py
#
# Central place for configuration that must not be hard-coded in the modules.
# Values are read from the .env file so each user can keep their own API key
# outside of the source code.

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from the project root, regardless of the current working directory
ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

_client = None


def get_api_key():
    """Return the OpenAI API key from the environment, or raise a clear error."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or api_key == "YOUR_API_KEY" or api_key.startswith("sk-your"):
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and set "
            "OPENAI_API_KEY to your own key from https://platform.openai.com/api-keys"
        )

    return api_key


def get_openai_client():
    """Return a shared OpenAI client built from the key in .env."""
    global _client

    if _client is None:
        _client = OpenAI(api_key=get_api_key())

    return _client
