import json
import os
from typing import Optional, Any

from dotenv import load_dotenv, set_key, dotenv_values

from plugins.utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """
    A class to manage dynamic access to environment variables.
    Uses properties to ensure values are always up to date.
    """

    def __init__(self, env_path: str = ""):
        self.env_path = env_path
        load_dotenv(env_path)

    def _get_current_value(self, key: str, default: Any, convert_type: type = str) -> Any:
        """Get current value from environment with proper type conversion"""
        try:
            value = os.environ.get(key, default)
            if convert_type == int:
                return int(value)
            return value
        except (ValueError, TypeError):
            return default

    # Dynamic property getters for all settings
    @property
    def OWNER_ID(self) -> int:
        return self._get_current_value("OWNER_ID", 0, int)

    @property
    def TG_BOT_TOKEN(self) -> str:
        return self._get_current_value("TG_BOT_TOKEN", "")

    @property
    def APP_ID(self) -> int:
        return self._get_current_value("APP_ID", 0, int)

    @property
    def API_HASH(self) -> str:
        return self._get_current_value("API_HASH", "")

    @property
    def TG_BOT_WORKERS(self) -> int:
        return self._get_current_value("TG_BOT_WORKERS", 1, int)

    @property
    def OWNER_TAG(self) -> str:
        return self._get_current_value("OWNER_TAG", "")

    @property
    def CHANNEL1(self) -> int:
        return self._get_current_value("CHANNEL1", 0, int)

    @property
    def CHANNEL2(self) -> int:
        return self._get_current_value("CHANNEL2", 0, int)

    @property
    def CUSTOM_MESSAGE(self) -> str:
        return self._get_current_value("CUSTOM_MESSAGE", "")

    @property
    def CUSTOM_MESSAGE_TEMP(self) -> str:
        return self._get_current_value("CUSTOM_MESSAGE_TEMP", "")

    @property
    def EMBEDEZ_API_KEY(self) -> str:
        return self._get_current_value("EMBEDEZ_API_KEY", "")

    @property
    def PORT(self) -> str:
        return self._get_current_value("PORT", "8080")

    @property
    def EMOJI(self) -> str:
        return self._get_current_value("EMOJI", "")

    def update_env_value(self, key: str, value: str) -> bool:
        """
        Update a value in the .env file and reload environment.

        Args:
            key: The environment variable key to update
            value: The new value to set

        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            config = dotenv_values(self.env_path)

            if key in config:
                set_key(self.env_path, key, value)
                load_dotenv(self.env_path, override=True)
                os.environ[key] = value
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating environment value: {e}")
            return False

    def get_all_values(self) -> Optional[str]:
        """
        Get all current environment values as JSON string.

        Returns:
            str: JSON string of current environment values or None if error occurs
        """
        try:
            load_dotenv(self.env_path, override=True)
            config = dotenv_values(self.env_path)
            return json.dumps(config, indent=3)
        except Exception as e:
            logger.error(f"Error getting environment values: {e}")
            return None


# Create a global instance of the settings manager
settings = SettingsManager(env_path="./.env")
