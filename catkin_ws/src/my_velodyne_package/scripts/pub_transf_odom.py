#!/usr/bin/env python
import rospy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from kafka import KafkaProducer
import json
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
            "orientation": {"x": q_B[1], "y": q_B[2], "z": q_B[3], "w": q_B[0]}
        }
        self.producer.send('odometry_topic', json.dumps(odometry_data))

    def get_transformed_pose(self, msg):
        position = msg.pose.pose.position
        cur_pos = np.array([position.x, position.y])
        trans_pos = self.transform_point(cur_pos)

        orientation = msg.pose.pose.orientation
        q_A = [orientation.w, orientation.x, orientation.y, orientation.z]
        q_B = self.transform_orientation(q_A)

        return trans_pos, q_B

    def transform_orientation(self, q_A):
        # Convert quaternion to Euler angles
        roll_A, pitch_A, yaw_A = self.quat_to_euler(q_A)

        # Applying 2D transformation to yaw angle (Z-angle)
        theta_B = self.loaded_homograpy_mat[0, 0] * yaw_A + self.loaded_homograpy_mat[0, 1]

        # Convert back to quaternion
        q_B = self.euler_to_quat(roll_A, pitch_A, theta_B)

        return q_B

    def transform_point(self, pt):
        h_pt = np.append(pt, 1)  # Homogeneous coordinates
        transformed = np.matmul(self.loaded_homograpy_mat, h_pt)  # Transformation
        transformed /= transformed[2]  # Convert to homogeneous coordinates
        return transformed[:2]  # Remove the last element (1) and return

    def quat_to_euler(self, q):
        # Ensure the quaternion array is of shape (4,)
        q = np.array(q).flatten()
        qw, qx, qy, qz = q

        # Calculate Euler angles
        roll = np.arctan2(2*(qw*qx + qy*qz), 1 - 2*(qx**2 + qy**2))
        pitch = np.arcsin(2*(qw*qy - qz*qx))
        yaw = np.arctan2(2*(qw*qz + qx*qy), 1 - 2*(qy**2 + qz**2))

        return roll, pitch, yaw

    def euler_to_quat(self, roll, pitch, yaw):
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        return qw, qx, qy, qz

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    node = ListenerNode()
    node.run()