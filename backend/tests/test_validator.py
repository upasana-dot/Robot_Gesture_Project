
import pytest

from app.planning.validator import validate_plan


def valid_plan():
    return [
        {"action": "approach", "object_name": "red_cube"},
        {"action": "grasp", "object_name": "red_cube"},
        {"action": "lift", "object_name": "red_cube"},
        {
            "action": "move_to",
            "object_name": "red_cube",
            "target": "blue_zone",
        },
        {
            "action": "release",
            "object_name": "red_cube",
            "target": "blue_zone",
        },
    ]


def test_valid_plan():
    result = validate_plan(valid_plan())

    assert len(result) == 5
    assert result[0]["step_number"] == 1
    assert result[-1]["action"] == "release"


def test_empty_plan_rejected():
    with pytest.raises(ValueError):
        validate_plan([])


def test_unsupported_action_rejected():
    actions = valid_plan()
    actions[0]["action"] = "fly"

    with pytest.raises(ValueError):
        validate_plan(actions)


def test_grasp_before_approach_rejected():
    actions = valid_plan()
    actions[0], actions[1] = actions[1], actions[0]

    with pytest.raises(ValueError):
        validate_plan(actions)


def test_missing_target_rejected():
    actions = valid_plan()
    actions[3].pop("target")

    with pytest.raises(ValueError):
        validate_plan(actions)
