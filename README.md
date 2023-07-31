# Robot_Localization
Robot_Localization


cd /catkin_make/src

catkin_create_pkg my_velodyne_package rospy sensor_msgs

cd my_velodyne_package/scripts

chmod +x point_cloud_subscribe.py

cd ~/catkin_ws
catkin_make

source devel/setup.bash


rosrun my_velodyne_package point_cloud_subscribe.py
