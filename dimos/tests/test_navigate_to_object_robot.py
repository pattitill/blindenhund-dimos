import os
import time
import sys
import argparse
import threading
from reactivex import Subject, operators as RxOps

from dimos.robot.unitree.unitree_go2 import UnitreeGo2
from dimos.robot.unitree.unitree_ros_control import UnitreeROSControl
from dimos.robot.unitree.unitree_skills import MyUnitreeSkills
from dimos.web.robot_web_interface import RobotWebInterface
from dimos.utils.logging_config import logger
from dimos.skills.navigation import Navigate
import tests.test_header

def parse_args():
    parser = argparse.ArgumentParser(description='Navigate to an object using Qwen vision.')
    parser.add_argument('--object', type=str, default="chair",
                        help='Name of the object to navigate to (default: chair)')
    parser.add_argument('--distance', type=float, default=1.0,
                        help='Desired distance to maintain from object in meters (default: 0.8)')
    parser.add_argument('--timeout', type=float, default=60.0,
                        help='Maximum navigation time in seconds (default: 30.0)')
    return parser.parse_args()

def main():
    # Get command line arguments
    args = parse_args()
    object_name = args.object  # Object to navigate to
    distance = args.distance   # Desired distance to object
    timeout = args.timeout     # Maximum navigation time
    
    print(f"Initializing Unitree Go2 robot for navigating to a {object_name}...")
    
    # Initialize the robot with ROS control and skills
    robot = UnitreeGo2(
        ip=os.getenv('ROBOT_IP'),
        ros_control=UnitreeROSControl(),
        skills=MyUnitreeSkills(),
    )

    # Add and create instance of NavigateToObject skill
    robot_skills = robot.get_skills()
    robot_skills.add(Navigate)
    robot_skills.create_instance("Navigate", robot=robot)

    # Set up tracking and visualization streams
    object_tracking_stream = robot.object_tracking_stream
    viz_stream = object_tracking_stream.pipe(
        RxOps.share(),
        RxOps.map(lambda x: x["viz_frame"] if x is not None else None),
        RxOps.filter(lambda x: x is not None),
    )

    # The local planner visualization stream is created during robot initialization
    local_planner_stream = robot.local_planner_viz_stream

    local_planner_stream = local_planner_stream.pipe(
        RxOps.share(),
        RxOps.map(lambda x: x if x is not None else None),
        RxOps.filter(lambda x: x is not None),
    )
    
    try:
        # Set up web interface
        logger.info("Initializing web interface")
        streams = {
            # "robot_video": video_stream,
            "object_tracking": viz_stream,
            "local_planner": local_planner_stream
        }
        
        web_interface = RobotWebInterface(
            port=5555,
            **streams
        )
        
        # Wait for camera and tracking to initialize
        print("Waiting for camera and tracking to initialize...")
        time.sleep(3)
        
        def navigate_to_object():
            try:
                result = robot_skills.call("Navigate", 
                                          robot=robot,
                                          query=object_name,
                                          timeout=timeout)
                print(f"Navigation result: {result}")
            except Exception as e:
                print(f"Error during navigation: {e}")
        
        navigate_thread = threading.Thread(
            target=navigate_to_object,
            daemon=True
        )
        navigate_thread.start()
        
        print(f"Navigating to {object_name} with desired distance {distance}m and timeout {timeout}s...")
        print("Web interface available at http://localhost:5555")
        
        # Start web server (blocking call)
        web_interface.run()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error during navigation test: {e}")
    finally:
        print("Test completed")
        robot.cleanup()


if __name__ == "__main__":
    main()