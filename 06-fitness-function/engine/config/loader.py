import json
import logging
import sys

logger = logging.getLogger(__name__)


def deep_update(d: dict, u: dict) -> dict:
    """
    Recursively merge two dictionaries.
    This is used to overlay specific document rules (e.g., SAD, PAD)
    on top of the global governance rules.
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deep_update(d.get(k, {}), v)
        elif isinstance(v, list) and isinstance(d.get(k), list):
            # Extend lists instead of replacing, avoiding duplicates
            d[k] = d[k] + [item for item in v if item not in d[k]]
        else:
            d[k] = v
    return d


def load_schema(schema_path: str) -> dict:
    """
    Load and parse a JSON schema file.
    Terminates the program if the file cannot be found.
    """
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical("Schema file '%s' not found.", schema_path)
        sys.exit(1)
