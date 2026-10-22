import pybullet as p

from app.simulation.robot import RobotController


class TaskExecutor:
    def __init__(self, world):
        self.world = world
        self.robot = RobotController(world)

    def execute(self, actions):
        results = []

        for action in actions:
            result = self.execute_action(action)
            results.append(result)

            if not result["success"]:
                break

        return results

    def execute_action(self, action):
        action_name = action["action"]
        object_name = action.get("object_name")
        target = action.get("target")

        try:
            # 1. Approach the requested cube.
            if action_name == "approach":
                if object_name not in self.world.cubes:
                    return self._failure(
                        action_name,
                        f"Unknown object: {object_name}",
                    )

                cube_id = self.world.cubes[object_name]
                cube_position, _ = p.getBasePositionAndOrientation(
                    cube_id,
                    physicsClientId=self.world.client,
                )

                destination = [
                    cube_position[0],
                    cube_position[1],
                    cube_position[2] + 0.06,
                ]

                result = self.robot.move_to(destination)

            # 2. Grasp the cube.
            elif action_name == "grasp":
                result = self.robot.grasp(object_name)

            # 3. Lift the grasped cube.
            elif action_name == "lift":
                if object_name not in self.world.cubes:
                    return self._failure(
                        action_name,
                        f"Unknown object: {object_name}",
                    )

                cube_id = self.world.cubes[object_name]
                cube_before = p.getBasePositionAndOrientation(
                    cube_id,
                    physicsClientId=self.world.client,
                )[0]

                end_state = p.getLinkState(
                    self.robot.robot_id,
                    self.robot.end_effector_link,
                    computeForwardKinematics=True,
                    physicsClientId=self.world.client,
                )
                end_position = end_state[4]

                destination = [
                    end_position[0],
                    end_position[1],
                    end_position[2] + 0.15,
                ]

                result = self.robot.move_to(destination)

                cube_after = p.getBasePositionAndOrientation(
                    cube_id,
                    physicsClientId=self.world.client,
                )[0]

                lifted = cube_after[2] > cube_before[2] + 0.03
                result["cube_lifted"] = lifted
                result["success"] = result["success"] and lifted

                if not lifted:
                    result["error"] = "Cube height did not increase enough"

            # 4. Move the grasped cube above a target zone.
            elif action_name == "move_to":
                if target not in self.world.targets:
                    return self._failure(
                        action_name,
                        f"Unknown target: {target}",
                    )

                target_position = self.world.targets[target]

                destination = [
                    target_position[0],
                    target_position[1],
                    target_position[2] + 0.08,
                ]

                result = self.robot.move_to(destination)

            # 5. Release the cube.
            elif action_name == "release":
                result = self.robot.release(object_name)

            else:
                return self._failure(
                    action_name,
                    f"Unsupported action: {action_name}",
                )

            return {
                "action": action_name,
                "object_name": object_name,
                "target": target,
                **result,
            }

        except Exception as exc:
            return self._failure(action_name, str(exc))

    @staticmethod
    def _failure(action_name, message):
        return {
            "action": action_name,
            "success": False,
            "error": message,
        }