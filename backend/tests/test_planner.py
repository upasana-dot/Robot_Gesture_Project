from app.ai.planner import fallback_plan


def test_pick_and_place_sequence():
    actions = fallback_plan(
        "Pick up the red cube and move it to the blue zone"
    )

    assert [a["action"] for a in actions] == [
        "approach",
        "grasp",
        "lift",
        "move_to",
        "release",
    ]

    assert actions[0]["object_name"] == "red_cube"
    assert actions[-1]["target"] == "blue_zone"