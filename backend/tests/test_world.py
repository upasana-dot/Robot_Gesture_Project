from app.simulation.world import RobotWorld


def test_world_creates_robot_and_objects():
    world = RobotWorld(gui=False)

    try:
        assert world.robot_id >= 0
        assert len(world.cubes) == 3
        assert "blue_zone" in world.targets
    finally:
        world.close()