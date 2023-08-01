# Robot_Localization
## Robot_Localization and pose update with kafka

### scout setting
1. docker bridge setting
```
# terminal 1
cd /ROS
docker start net_ros1_bridge
docker exec -it net_ros1_bridge /bin/bash
cd root/
./ros1_bridge.sh
```
```
# terminal 2
docker exec -it net_ros1_bridge /bin/bash
cd root/
./ros2_bridge.sh
```
2. docker lidar setting
```
# local
cd /ROS
./can_lidar_setting.sh
docker start net_ros2_lidar
docker exec -it net_ros2_lidar /bin/bash
```

```
# docker
cd /ROS
./docker_lidar_setting.sh
source ~/.bashrc
ros2 launch velodyne velodyne-all-nodes-VLP16-launch.py
```

3. hdl_localization_tutorial
```
# terminal 1
xhost +local:docker
docker start hdl
docker exec -it hdl /bin/bash
source /opt/ros/melodic/setup.bash

cd ~/catkin_ws
catkin_make
source devel/setup.bash
rosparam set use_sim_time true
roslaunch hdl_localization hdl_localization.launch
```
```
# terminal 2 
docker exec -it hdl /bin/bash
source /opt/ros/melodic/setup.bash
cd hdl_localization/rviz
rviz -d hdl_localization.rviz
```
___
### Send to Kafka
```
cd /catkin_make/src
```

if exist, pass
```
catkin_create_pkg my_velodyne_package rospy sensor_msgs
```

```
cd my_velodyne_package/scripts
chmod +x pub_transf_odom.py
```

```
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

```
rosrun my_velodyne_package pub_transf_odom.py
```

## Send to omniverse
```
mv robot_localization.py /isaac-sim/extension_examples/hello_world
rm -rf hello_world.py
mv robot_localization.py hello_world.py
```