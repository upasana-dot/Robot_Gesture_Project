import time

import pybullet as p
import pybullet_data


class RobotWorld:
    def __init__(self, gui=True):
        self.gui = gui
        self.client = p.connect(
            p.GUI if gui else p.DIRECT
        )

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")

        self.robot_id = p.loadURDF(
            "kuka_iiwa/model.urdf",
            basePosition=[0, 0, 0],
            useFixedBase=True,
        )

        self.cubes = {}
        self.targets = {
            "blue_zone": [0.45, 0.25, 0.04],
            "red_zone": [0.45, -0.25, 0.04],
            "green_zone": [0.35, 0.0, 0.04],
            "table": [0.50, 0.0, 0.04],
        }

        self._create_cubes()
        self._create_targets()

    def _create_cubes(self):
        colors = {
            "red_cube": [1, 0, 0, 1],
            "blue_cube": [0, 0, 1, 1],
            "green_cube": [0, 1, 0, 1],
        }

        positions = {
            "red_cube": [0.50, -0.12, 0.04],
            "blue_cube": [0.50, 0.00, 0.04],
            "green_cube": [0.50, 0.12, 0.04],
        }

        for name, color in colors.items():
            visual = p.createVisualShape(
                p.GEOM_BOX,
                halfExtents=[0.025, 0.025, 0.025],
                rgbaColor=color,
            )

            collision = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=[0.025, 0.025, 0.025],
            )

            self.cubes[name] = p.createMultiBody(
                baseMass=0.1,
                baseCollisionShapeIndex=collision,
                baseVisualShapeIndex=visual,
                basePosition=positions[name],
            )

    def _create_targets(self):
        for name, pos in self.targets.items():
            if name == "table":
                continue

            visual = p.createVisualShape(
                p.GEOM_BOX,
                halfExtents=[0.06, 0.06, 0.005],
                rgbaColor=[0.2, 0.5, 1, 0.35],
            )

            p.createMultiBody(
                baseMass=0,
                baseVisualShapeIndex=visual,
                basePosition=pos,
            )

    def step(self, count=120):
        for _ in range(count):
            p.stepSimulation()
            if self.gui:
                time.sleep(1 / 240)

    def close(self):
        if p.isConnected(self.client):
            p.disconnect(self.client)