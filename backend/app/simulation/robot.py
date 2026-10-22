
import pybullet as p


class RobotController:
    def __init__(self, world):
        self.world = world
        self.robot_id = world.robot_id
        self.client = world.client
        self.end_effector_link = 6
        self.joint_indices = []

        joint_count = p.getNumJoints(
            self.robot_id,
            physicsClientId=self.client,
        )

        for joint_index in range(joint_count):
            info = p.getJointInfo(
                self.robot_id,
                joint_index,
                physicsClientId=self.client,
            )

            if info[2] != p.JOINT_FIXED:
                self.joint_indices.append(joint_index)

    def move_to(self, position):
        joint_positions = p.calculateInverseKinematics(
            self.robot_id,
            self.end_effector_link,
            position,
            physicsClientId=self.client,
        )

        for index, joint_index in enumerate(self.joint_indices):
            if index >= len(joint_positions):
                break

            p.setJointMotorControl2(
                self.robot_id,
                joint_index,
                p.POSITION_CONTROL,
                targetPosition=joint_positions[index],
                force=200,
                physicsClientId=self.client,
            )

        self.world.step(240)

        actual_position = p.getLinkState(
            self.robot_id,
            self.end_effector_link,
            computeForwardKinematics=True,
            physicsClientId=self.client,
        )[4]

        error = sum(
            (actual_position[i] - position[i]) ** 2
            for i in range(3)
        ) ** 0.5

        return {
            "success": error < 0.08,
            "target_position": list(position),
            "actual_position": list(actual_position),
            "position_error": error,
        }

    def grasp(self, object_name):
        if object_name not in self.world.cubes:
            return {
                "success": False,
                "error": f"Unknown object: {object_name}",
            }

        cube_id = self.world.cubes[object_name]

        end_state = p.getLinkState(
            self.robot_id,
            self.end_effector_link,
            computeForwardKinematics=True,
            physicsClientId=self.client,
        )
        end_position = end_state[4]
        end_orientation = end_state[5]

        cube_position, cube_orientation = (
            p.getBasePositionAndOrientation(
                cube_id,
                physicsClientId=self.client,
            )
        )

        distance = sum(
            (end_position[i] - cube_position[i]) ** 2
            for i in range(3)
        ) ** 0.5

        if distance > 0.10:
            return {
                "success": False,
                "error": (
                    f"End-effector is too far from {object_name}: "
                    f"{distance:.3f} m"
                ),
            }

        inverse_transform = p.invertTransform(
            end_position,
            end_orientation,
        )

        relative_position, relative_orientation = (
            p.multiplyTransforms(
                inverse_transform[0],
                inverse_transform[1],
                cube_position,
                cube_orientation,
            )
        )

        constraint_id = p.createConstraint(
            self.robot_id,
            self.end_effector_link,
            cube_id,
            -1,
            p.JOINT_FIXED,
            [0, 0, 0],
            relative_position,
            [0, 0, 0],
            parentFrameOrientation=relative_orientation,
            physicsClientId=self.client,
        )

        if not hasattr(self.world, "cube_constraints"):
            self.world.cube_constraints = {}

        self.world.cube_constraints[object_name] = constraint_id

        return {
            "success": True,
            "action": "grasp",
            "object_name": object_name,
        }

    def release(self, object_name):
        constraints = getattr(
            self.world, "cube_constraints", {}
        )
        constraint_id = constraints.pop(object_name, None)

        if constraint_id is None:
            return {
                "success": False,
                "error": f"{object_name} is not currently grasped",
            }

        p.removeConstraint(
            constraint_id,
            physicsClientId=self.client,
        )
        self.world.step(10)

        return {
            "success": True,
            "action": "release",
            "object_name": object_name,
        }
