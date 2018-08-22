import json

from .constants import CONFIG_FILE_NAME


def load_config():
    """Load and return the config from file."""
    with open(CONFIG_FILE_NAME) as f:
        return json.load(f)
