import json
from json import JSONDecodeError
from pathlib import Path
from typing import Optional


class ConfigurationService:
    def __init__(self, config_file):
        self.conf_file = Path(config_file)
        self._read_config()

    def _get_key(self, key):
        return self.config.get(key)

    def _get_string_key(self, key) -> Optional[str]:
        value = self._get_key(key)
        if not isinstance(value, str):
            return None
        return value

    def get_string_key(self, key):
        value = self._get_string_key(key)
        if not value:
            raise Exception(f"Key {key} is not set")
        return value

    def _read_config(self):
        try:
            with self.conf_file.open() as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError:
            print(f"Configuration file does not exist at {self.conf_file.resolve()}")
            raise
        except JSONDecodeError:
            print(f"Configuration file is corrupted at {self.conf_file.resolve()}")
            raise
