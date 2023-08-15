#!/usr/bin/env python
import rospy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from kafka import KafkaProducer
import json
from scipy.spatial.transform import Rotation
import numpy as np

class ListenerNode:
    def __init__(self):
        rospy.init_node('listener', anonymous=True)
        self.pub = rospy.Publisher('/velodyne_points_again', PointCloud2, queue_size=10)
        self.producer = KafkaProducer(bootstrap_servers=['203.250.148.120:20517'], api_version=(0,11,5))

        # Load homography matrix here during initialization
        self.loaded_homograpy_mat = np.load('/root/catkin_ws/src/Robot_Localization/homography_matrix.npy')

        rospy.Subscriber("/velodyne_points", PointCloud2, self.callback)
        rospy.Subscriber("/odom", Odometry, self.odometry_callback)

    def callback(self, data):
        self.pub.publish(data)

    def odometry_callback(self, msg):
        # Get transformed position and orientation
        trans_pos, q_B = self.get_transformed_pose(msg)

        # Package and send data as JSON
        odometry_data = {
            "position": {"x": trans_pos[0], "y": trans_pos[1]},
            "orientation": {"x": q_B[0], "y": q_B[1], "z": q_B[2], "w": q_B[3]}
        }
        self.producer.send('odometry_topic', json.dumps(odometry_data))

    def get_transformed_pose(self, msg):
        position = msg.pose.pose.position
        cur_pos = np.array([position.x, position.y])
        trans_pos = self.transform_point(cur_pos)

        orientation = msg.pose.pose.orientation
        q_A = [orientation.x, orientation.y, orientation.z, orientation.w]
        new_rotation_matrix = self.transform_orientation(q_A)
        new_rotation = Rotation.from_matrix(new_rotation_matrix)
        q_B = new_rotation.as_quat()

        return trans_pos, q_B

    def transform_orientation(self, q_A):
        rotation_A = Rotation.from_quat(q_A)
        rotation_matrix_A = rotation_A.as_matrix()
        return self.loaded_homograpy_mat[:2, :2] @ rotation_matrix_A[:2, :2]

    def transform_point(self, pt):
        h_pt = np.append(pt, 1)  # Homogeneous coordinates
        transformed = np.matmul(self.loaded_homograpy_mat, h_pt)  # Transformation
        transformed /= transformed[2]  # Convert to homogeneous coordinates
        return transformed[:2]  # Remove the last element (1) and return

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    node = ListenerNode()
    node.run()