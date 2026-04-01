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

install(PROGRAMS
  rovermk2_description/steerdeg_pub.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME steerdeg_pub
)

install(PROGRAMS
  rovermk2_description/controller.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME controller
)

ament_package()
