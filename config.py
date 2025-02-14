import json
import os

from dotenv import load_dotenv, set_key, dotenv_values

# Load environment variables
load_dotenv()

# Owner Id configuration
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Bot configuration
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "1"))
OWNER_TAG = os.environ.get("OWNER_TAG", "")

# Additional settings
CHANNEL1 = int(os.environ.get("CHANNEL1", 0))
CHANNEL2 = int(os.environ.get("CHANNEL2", 0))
GROUP1 = int(os.environ.get("GROUP1", 0))
GROUP2 = int(os.environ.get("GROUP2", 0))
CUSTOM_MESSAGE = os.environ.get("CUSTOM_MESSAGE", "")
CUSTOM_MESSAGE_TEMP = os.environ.get("CUSTOM_MESSAGE_TEMP", "")
EMBEDEZ_API_KEY = os.environ.get("EMBEDEZ_API_KEY", "")
PORT = os.environ.get("PORT", "8080")
EMOJI = os.environ.get("EMOJI", "")
env_path = "./.env"


# Function to update .env file
def update_env_value(key: str, value: str) -> bool:
    # Load existing .env values
    config = dotenv_values(env_path)

    # Check if key exists
    if key in config:
        set_key(env_path, key, value)  # ✅ Corrected argument names
        load_dotenv(env_path, override=True)  # Reload to reflect changes
        os.environ[key] = value  # Ensure the new value is accessible at runtime
        return True

    return False


def get_dot_env_values():
    config = dotenv_values(env_path)
    return json.dumps(config, indent=3)
