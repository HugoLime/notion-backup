import json
from json import JSONDecodeError
from pathlib import Path
from typing import Optional

CONFIGURATION_FILE_NAME = ".notion_backup.conf"
DEFAULT_CONFIG = {"version": 1}


class ConfigurationService:
    def __init__(self, config_path: Path = Path.home()):
        self.conf_file = config_path / CONFIGURATION_FILE_NAME
        self._read_config()

    def _get_key(self, key):
        return self.config.get(key)

    def get_string_key(self, key) -> Optional[str]:
        value = self._get_key(key)
        if not isinstance(value, str):
            return None
        return value

    def write_key(self, key, value):
        self.config[key] = value
        self._save_config()

    def _create_default_config(self):
        self.config = DEFAULT_CONFIG
        self._save_config()

    def _read_config(self):
        try:
            with self.conf_file.open() as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError:
            print("Configuration file does not exist, creating")
            self.conf_file.touch(mode=0o700, exist_ok=True)
            self._create_default_config()
        except JSONDecodeError:
            print("Configuration file is corrupted, recreating it")
            self._create_default_config()

    def _save_config(self):
        with self.conf_file.open("w") as conf_file_handle:
            json.dump(self.config, conf_file_handle, indent=4, sort_keys=True)
            conf_file_handle.write("\n")  # Add trailing newline
