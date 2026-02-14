import os
from pathlib import Path
from typing import Any, Dict


class Config:
    _instance = None
    _properties: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            config_path = Path(__file__).parents[4] / 'resources' / 'config.properties'
            if not config_path.exists():
                raise ImportError(f'{config_path}: config.properties not found')
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        cls._properties[key] = value
        return cls._instance

    @property
    def properties(self) -> dict[str, Any]:
        return self._properties

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        # Allow overriding config.properties via environment variables (useful for CI / Docker / different backends).
        env_val = os.getenv(key) or os.getenv(key.upper())
        if env_val is not None:
            return env_val
        return Config().properties.get(key, default_value)
