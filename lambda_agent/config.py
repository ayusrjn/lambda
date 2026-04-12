import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Try loading from global config first
    global_env = Path.home() / ".config" / "lambda-agent" / "config.env"
    if global_env.exists():
        load_dotenv(dotenv_path=global_env)

    # Allow local .env to override global configs
    load_dotenv(override=True)
except ImportError:
    print(
        "Warning: python-dotenv not installed. If you are using a .env file, it will not be loaded."
    )

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.1-pro-preview")

# Models available for /models switching
AVAILABLE_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
]
