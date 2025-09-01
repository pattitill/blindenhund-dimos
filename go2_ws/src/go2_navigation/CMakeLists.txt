cmake_minimum_required(VERSION 3.8)
project(go2_navigation)

find_package(ament_cmake REQUIRED)

# Ordner (wie gehabt)
install(
  DIRECTORY config maps
  DESTINATION share/${PROJECT_NAME}
)

# Launchfiles direkt ins Paket-Root (ohne /launch)
install(
  FILES
    navigate.launch.py
    slam.launch.py
  DESTINATION share/${PROJECT_NAME}
)

ament_package()