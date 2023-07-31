#!/usr/bin/env python

import rospy
from sensor_msgs.msg import PointCloud2

def callback(data):
    pub.publish(data)

def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/velodyne_points", PointCloud2, callback)

    global pub
    pub = rospy.Publisher('/velodyne_points', PointCloud2, queue_size=10)

    rospy.spin()

if __name__ == '__main__':
    listener()