import math
import os
import time
import threading
from dimos.robot.unitree.unitree_go2 import UnitreeGo2
from dimos.robot.unitree.unitree_ros_control import UnitreeROSControl
from dimos.web.websocket_vis.server import WebsocketVis
from dimos.web.websocket_vis.helpers import vector_stream
from dimos.robot.global_planner.planner import AstarPlanner
from dimos.types.costmap import Costmap
from dimos.types.vector import Vector
from reactivex import operators as ops
import argparse
import pickle
import reactivex as rx
from dimos.web.robot_web_interface import RobotWebInterface


def parse_args():
    parser = argparse.ArgumentParser(description="Simple test for vis.")
    parser.add_argument(
        "--live",
        action="store_true",
    )
    parser.add_argument(
        "--port", type=int, default=5555, help="Port for web visualization interface"
    )
    return parser.parse_args()


def setup_web_interface(robot, port=5555):
    """Set up web interface with robot video and local planner visualization"""
    print(f"Setting up web interface on port {port}")
    
    # Get video stream from robot
    video_stream = robot.video_stream_ros.pipe(
        ops.share(),
        ops.map(lambda frame: frame),
        ops.filter(lambda frame: frame is not None),
    )
    
    # Get local planner visualization stream
    local_planner_stream = robot.local_planner_viz_stream.pipe(
        ops.share(),
        ops.map(lambda frame: frame),
        ops.filter(lambda frame: frame is not None),
    )
    
    # Create web interface with streams
    web_interface = RobotWebInterface(
        port=port,
        robot_video=video_stream,
        local_planner=local_planner_stream
    )
    
    return web_interface


def main():
    args = parse_args()

    websocket_vis = WebsocketVis()
    websocket_vis.start()
    
    web_interface = None

    if args.live:
        ros_control = UnitreeROSControl(node_name="web_nav_test", mock_connection=False)
        robot = UnitreeGo2(ros_control=ros_control, ip=os.getenv("ROBOT_IP"))
        planner = robot.global_planner

        websocket_vis.connect(vector_stream("robot", lambda: robot.ros_control.transform_euler_pos("base_link")))
        websocket_vis.connect(robot.ros_control.topic("map", Costmap).pipe(ops.map(lambda x: ["costmap", x])))
        
        # Also set up the web interface with both streams
        if hasattr(robot, 'video_stream_ros') and hasattr(robot, 'local_planner_viz_stream'):
            web_interface = setup_web_interface(robot, port=args.port)
            
            # Start web interface in a separate thread
            viz_thread = threading.Thread(target=web_interface.run, daemon=True)
            viz_thread.start()
            print(f"Web interface available at http://localhost:{args.port}")

    else:
        pickle_path = f"{__file__.rsplit('/', 1)[0]}/mockdata/vegas.pickle"
        print(f"Loading costmap from {pickle_path}")
        planner = AstarPlanner(
            get_costmap=lambda: pickle.load(open(pickle_path, "rb")),
            get_robot_pos=lambda: Vector(5.0, 5.0),
            set_local_nav=lambda x: time.sleep(1) and True,
        )

    def msg_handler(msgtype, data):
        if msgtype == "click":
            target = Vector(data["position"])
            try:
                planner.set_goal(target)
            except Exception as e:
                print(f"Error setting goal: {e}")
                return

    def threaded_msg_handler(msgtype, data):
        thread = threading.Thread(target=msg_handler, args=(msgtype, data))
        thread.daemon = True
        thread.start()

    websocket_vis.connect(planner.vis_stream())
    websocket_vis.msg_handler = threaded_msg_handler

    print(f"WebSocket server started on port {websocket_vis.port}")
    print(planner.get_costmap())

    planner.plan(Vector(-4.8, -1.0))  # plan a path to the origin

    def fakepos():
        # Simulate a fake vector position change (to test realtime rendering)
        vec = Vector(math.sin(time.time()) * 2, math.cos(time.time()) * 2, 0)
        print(vec)
        return vec

    #    if not args.live:
    #        websocket_vis.connect(rx.interval(0.05).pipe(ops.map(lambda _: ["fakepos", fakepos()])))

    try:
        # Keep the server running
        while True:
            time.sleep(0.1)
            pass
    except KeyboardInterrupt:
        print("Stopping WebSocket server...")
        websocket_vis.stop()
        print("WebSocket server stopped")


if __name__ == "__main__":
    main()
