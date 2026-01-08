from pathlib import Path
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

class ConfigError(Exception):
    pass


def load_config(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ConfigError("Config must be a YAML object")

    return data

def get_env(name: str, required: bool = True) -> str | None:
    value = os.getenv(name)
    if required and not value:
        raise ConfigError(f"Missing environment variable: {name}")
    return value

