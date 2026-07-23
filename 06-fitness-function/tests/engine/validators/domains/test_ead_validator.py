import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _global_rules():
    with open(
        os.path.join(ROOT, "00-governance", "schemas", "base.schema.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f).get("x-global-config", {})
