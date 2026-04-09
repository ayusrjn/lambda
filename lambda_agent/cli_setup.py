import getpass
from pathlib import Path
import os


def run_setup() -> tuple[str, str]:
    print("\n" + "=" * 56)
    print(" Welcome to Lambda Agent Setup!")
    print(" This appears to be your first time running Lambda.")
    print("=" * 56 + "\n")
    print("Lambda requires a Gemini API Key to function.")
    print("You can get one for free at: https://aistudio.google.com/app/apikey\n")

    api_key = ""
    while not api_key:
        api_key = getpass.getpass("Enter your Gemini API Key: ").strip()
        if not api_key:
            print("API Key cannot be empty. Please try again.")

    default_model = "gemini-3.0-flash-preview"
    model_name = input(f"Enter model name (default: {default_model}): ").strip()
    if not model_name:
        model_name = default_model

    config_dir = Path.home() / ".config" / "lambda-agent"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.env"

    try:
        # Create or update the config file securely
        with open(config_file, "w") as f:
            f.write(f"API_KEY={api_key}\n")
            f.write(f"MODEL_NAME={model_name}\n")

        # Secure the file (rw for owner only)
        os.chmod(config_file, 0o600)

        print(f"\n✅ Setup complete! Configuration saved to {config_file}\n")
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        print("Continuing with in-memory configuration for this session.\n")

    return api_key, model_name
