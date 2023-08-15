# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.



# Note: checkout the required tutorials at https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/overview.html


# class HelloWorld(BaseSample):
#     def __init__(self) -> None:
#         super().__init__()
#         return

#     def setup_scene(self):

#         world = self.get_world()
#         world.scene.add_default_ground_plane()
#         return

#     async def setup_post_load(self):
#         return

#     async def setup_pre_reset(self):
#         return

#     async def setup_post_reset(self):
#         return

#     def world_cleanup(self):
#         return

import time
from omni.isaac.examples.base_sample import BaseSample
from omni.isaac.wheeled_robots.robots import WheeledRobot
from omni.kit.commands import execute
from kafka import KafkaConsumer, TopicPartition
import numpy as np
import json
from omni.isaac.core import World
import omni

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

        # Kafka Consumer Setup
        self.odom_consumer = KafkaConsumer(
            bootstrap_servers=['203.250.148.120:20517'],
            auto_offset_reset='earliest',
            group_id='mygroup',
            enable_auto_commit=False
        )
        self.topic = 'odometry_topic'


        return

    def setup_scene(self):

        self._my_world = self.get_world()
        self.stage = omni.usd.get_context().get_stage()
        map_asset_path ="/root/isaac-DT/5f_0919.usd"
        execute(
                "IsaacSimSpawnPrim",
                usd_path=map_asset_path,
                prim_path="/World/env_space",
                translation=(0,0,0),
                rotation=(0,90,90,0)
        )
        execute(
                "IsaacSimScalePrim",
                prim_path="/World/env_space",
                scale=(0.01,0.01,0.01),
        )
        agent_asset_path ="/root/isaac-DT/scout_v2.usd"
        self.agent = self._my_world.scene.add(
            WheeledRobot(
                prim_path="/World/scout_v2",
                name="my_scout_v2",
                wheel_dof_names=["front_left_wheel","rear_left_wheel","front_right_wheel","rear_right_wheel"],
                wheel_dof_indices=[0,1,2,3],
                create_robot=True,
                usd_path=agent_asset_path,
                position=np.array([-4, 0, 0.1]),
                orientation=np.array([1.0, 0.0, 0.0, 0.0]),
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._scout = self._world.scene.get_object("my_scout_v2")
        self._world.add_physics_callback("sending_actions", callback_fn=self.update_robot_pose_rotation)
        return

    def update_robot_pose_rotation(self, hi):
        # Poll for Kafka messages
        partitions = self.odom_consumer.partitions_for_topic(self.topic)
        last_offsets = {p: offset - 1 for p in partitions for offset in self.odom_consumer.end_offsets([TopicPartition(self.topic, p)]).values()}

        for p, last_offset in last_offsets.items():
            start_offset = max(0, last_offset - 1 + 1)
            tp = TopicPartition(self.topic, p)
            self.odom_consumer.assign([tp])
            self.odom_consumer.seek(tp, start_offset)
        start = time.time()
        messages = self.odom_consumer.poll(timeout_ms=1000)  # Wait for 1000ms

        if messages:
            for tp, msgs in messages.items():
                for message in msgs:
                    print("Received message: {}".format(message.value))
                    decoded_message = message.value.decode('utf-8')  # Decode the bytes to string
                    data = json.loads(decoded_message)  # Convert the JSON string to a dictionary

                    # Retrieve position and orientation
                    x = data['position']['x']
                    y = data['position']['y']
                    orientation = data['orientation']
                    q_x = orientation['x']
                    q_y = orientation['y']
                    q_z = orientation['z']
                    q_w = orientation['w']

                    execute(
                        "IsaacSimTeleportPrim",
                        prim_path="/World/scout_v2",
                        translation=(x, y, 0.27119),
                        rotation=(q_x, q_y, q_z, q_w),
                    )
        else:
            print("No message received within timeout period")
        print("time :", time.time() - start)

        return



    async def setup_pre_reset(self):
        return

    async def setup_post_reset(self):
        return

    def world_cleanup(self):
        return

