
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load API key from backend/.env
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your backend/.env file."
    )


# Initialize Gemini client with controlled timeout and retries
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(
            attempts=1
        )
    )
)

# Model configuration
MODEL_NAME = "gemini-3.8-flash"


def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini and return its response.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
