cmake_minimum_required(VERSION 3.8)
project(go2_gazebo)

find_package(ament_cmake REQUIRED)

# Installiere die Launchfiles
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Installiere die Welten
install(
  DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()