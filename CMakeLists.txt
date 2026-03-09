cmake_minimum_required(VERSION 3.8)
project(rovermk2_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes launch config worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    rovermk2_description/cmdvel_controller.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME cmd_vel_converter
)

ament_package()
