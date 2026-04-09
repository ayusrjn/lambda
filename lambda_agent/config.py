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
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.1-flash-lite-preview")
