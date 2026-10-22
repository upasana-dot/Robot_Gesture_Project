
import json
import re

from app.ai.model import generate_text


ALLOWED_OBJECTS = {
    "red_cube", "blue_cube", "green_cube"
}

ALLOWED_TARGETS = {
    "table", "blue_zone", "red_zone", "green_zone"
}

ALLOWED_ACTIONS = {
    "approach", "grasp", "lift", "move_to", "release"
}


def normalize_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def fallback_plan(instruction: str) -> list[dict]:
    text = instruction.lower()

    # Identify the object
    object_name = next(
        (name for name in ALLOWED_OBJECTS if name in text),
        None,
    )

    if object_name is None:
        match = re.search(
            r"\b(red|blue|green)\s+(cube|block)\b",
            text,
        )
        if match:
            object_name = f"{match.group(1)}_cube"

    # Identify the target
    target = next(
        (name for name in ALLOWED_TARGETS if name in text),
        None,
    )

    if target is None:
        if re.search(r"\bblue\s+(box|area|zone)\b", text):
            target = "blue_zone"
        elif re.search(r"\bred\s+(box|area|zone)\b", text):
            target = "red_zone"
        elif re.search(r"\bgreen\s+(box|area|zone)\b", text):
            target = "green_zone"
        elif re.search(r"\btable\b", text):
            target = "table"

    # Validate object and target
    if object_name is None:
        raise ValueError(
            "Please specify a supported object: red, blue, or green cube."
        )

    if target is None:
        raise ValueError(
            "Please specify a target: table or a colored zone."
        )

    # Generate the pick-and-place sequence
    return [
        {"action": "approach", "object_name": object_name},
        {"action": "grasp", "object_name": object_name},
        {"action": "lift", "object_name": object_name},
        {
            "action": "move_to",
            "object_name": object_name,
            "target": target,
        },
        {
            "action": "release",
            "object_name": object_name,
            "target": target,
        },
    ]


def generate_plan(instruction: str) -> list[dict]:
    # Try the pretrained AI model first.
    # If its output is invalid, use the deterministic fallback.
    try:
        raw = generate_text(instruction)
        data = json.loads(raw)

        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")

        actions = data.get("actions")

        if not isinstance(actions, list) or not actions:
            raise ValueError("No actions returned.")

        return actions

    except Exception:
        return fallback_plan(instruction)
