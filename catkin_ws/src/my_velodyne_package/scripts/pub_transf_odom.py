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
        position = msg.pose.pose.position
        cur_pos = np.array([position.x, position.y])
        trans_pos = self.transform_point(cur_pos)
        position_dict = {"x": trans_pos[0], "y": trans_pos[1]}
        self.producer.send('odometry_topic', json.dumps(position_dict))

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
