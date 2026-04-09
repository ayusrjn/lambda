import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "Warning: python-dotenv not installed. If you are using a .env file, it will not be loaded."
    )

# Default to using Gemini
API_KEY = os.getenv("API_KEY")  # You can name this GEMINI_API_KEY in your .env
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

if not API_KEY:
    print("WARNING: API_KEY is not set in the environment or .env file.")
