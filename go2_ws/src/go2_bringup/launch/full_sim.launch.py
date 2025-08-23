from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # 1. Gazebo mit Roboter starten
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('go2_gazebo'),
                'launch',
                'gazebo.launch.py'
            )
        )
    )

    # 2. SLAM Toolbox starten
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('go2_navigation'),
                'slam.launch.py'
            )
        )
    )

    # 3. Nav2 starten
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('go2_navigation'),
                'navigate.launch.py'
            )
        )
    )

    # 4. DimOS Bridge starten
    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('dimos_ros_bridge'),
                'launch',
                'dimos_bridge.launch.py'
            )
        )
    )

    return LaunchDescription([
        gazebo_launch,
        slam_launch,
        nav2_launch,
        bridge_launch
    ])
