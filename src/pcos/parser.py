from pathlib import Path
import yaml
import sys


class ContractError(Exception):
    pass


REQUIRED_FIELDS = [
    "project",
    "deadline",
    "tickets",
    "definition_of_done",
]


def load_contract(path: Path) -> dict:
    if not path.exists():
        raise ContractError(f"Contract file not found: {path}")

    text = path.read_text()

    if not text.startswith("---"):
        raise ContractError("Contract must start with YAML frontmatter")

    try:
        _, yaml_block, _ = text.split("---", 2)
    except ValueError:
        raise ContractError("Invalid YAML frontmatter format")

    try:
        data = yaml.safe_load(yaml_block)
    except Exception as e:
        raise ContractError(f"Invalid YAML: {e}")

    validate_contract(data)
    return data


def validate_contract(data: dict) -> None:
    if not isinstance(data, dict):
        raise ContractError("Contract YAML must be an object")

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ContractError(f"Missing required field: {field}")

    if not isinstance(data["tickets"], list) or len(data["tickets"]) == 0:
        raise ContractError("tickets must be a non-empty list")

    for ticket in data["tickets"]:
        if "title" not in ticket:
            raise ContractError("Each ticket must have a title")


def read_input_text(path=None) -> str:
    if path:
        return path.read_text()
    else:
        return sys.stdin.read()