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
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")
PORT = os.environ.get("PORT", "8080")
