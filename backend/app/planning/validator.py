
from app.ai.planner import (
    ALLOWED_ACTIONS,
    ALLOWED_OBJECTS,
    ALLOWED_TARGETS,
)


def validate_plan(actions: list[dict]) -> list[dict]:
    if not isinstance(actions, list) or not actions:
        raise ValueError("Action plan cannot be empty.")

    cleaned = []
    object_states = {}

    for index, item in enumerate(actions, start=1):
        if not isinstance(item, dict):
            raise ValueError("Every action must be an object.")

        action = item.get("action")
        obj = item.get("object_name")
        target = item.get("target")

        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")

        if obj not in ALLOWED_OBJECTS:
            raise ValueError(f"Unsupported object: {obj}")

        if target is not None and target not in ALLOWED_TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        state = object_states.get(obj, "new")

        if action == "approach":
            if state != "new":
                raise ValueError(
                    f"Cannot approach {obj} in its current state."
                )
            if target is not None:
                raise ValueError("Approach action must not specify a target.")
            object_states[obj] = "approached"

        elif action == "grasp":
            if state != "approached":
                raise ValueError(
                    f"{obj} must be approached before grasping."
                )
            if target is not None:
                raise ValueError("Grasp action must not specify a target.")
            object_states[obj] = "grasped"

        elif action == "lift":
            if state != "grasped":
                raise ValueError(
                    f"{obj} must be grasped before lifting."
                )
            if target is not None:
                raise ValueError("Lift action must not specify a target.")
            object_states[obj] = "lifted"

        elif action == "move_to":
            if state != "lifted":
                raise ValueError(
                    f"{obj} must be lifted before moving."
                )
            if target is None:
                raise ValueError("move_to requires a valid target.")
            object_states[obj] = "moved"

        elif action == "release":
            if state != "moved":
                raise ValueError(
                    f"{obj} must be moved to a target before release."
                )
            if target is None:
                raise ValueError("release requires a valid target.")

            object_states[obj] = "released"

        cleaned.append({
            "step_number": index,
            "action": action,
            "object_name": obj,
            "target": target,
        })

    unfinished = [
        obj for obj, state in object_states.items()
        if state != "released"
    ]

    if unfinished:
        raise ValueError(
            "Plan must complete pick-and-place for: "
            + ", ".join(unfinished)
        )

    return cleaned
