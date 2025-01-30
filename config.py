import os

from dotenv import load_dotenv

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
EMBEDEZ_API_KEY = os.environ.get("EMBEDEZ_API_KEY", "")
PORT = os.environ.get("PORT", "8080")
