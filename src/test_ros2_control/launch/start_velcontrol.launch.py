from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command

# 封装终端指令相关类--------------
# from launch.actions import ExecuteProcess
# from launch.substitutions import FindExecutable
# 参数声明与获取-----------------
# from launch.actions import DeclareLaunchArgument
# from launch.substitutions import LaunchConfiguration
# 文件包含相关-------------------
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

# 分组相关----------------------
# from launch_ros.actions import PushRosNamespace
# from launch.actions import GroupAction
# 事件相关----------------------
# from launch.event_handlers import OnProcessStart, OnProcessExit
# from launch.actions import ExecuteProcess, RegisterEventHandler,LogInfo
# 获取功能包下share目录路径-------
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    urdfname = "t1bot_with_velcontrol.xacro"
    pkgpath = get_package_share_directory("test_ros2_control")
    t1bot_desc = os.path.join(pkgpath, "urdf", urdfname)
    defaule_rviz_config_path = os.path.join(pkgpath, "config", "show_model.rviz")
    robot_description_content = Command(["xacro ", t1bot_desc])
    robot_description = {"robot_description": robot_description_content}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {  # 使用 Command 动态调用 xacro 命令解析文件
                "robot_description": Command(["xacro ", t1bot_desc])
            },
            {"use_sim_time": True},
        ],
    )

    gazebo_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory("ros_gz_sim"),
                    "launch",
                    "gz_sim.launch.py",
                ),
            ]
        ),
        launch_arguments=[
            (
                "gz_args",
                "empty.sdf -r --physics-engine gz-physics-bullet-featherstone-plugin",
            )
        ],
    )

    addrobot_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "1.0",
            "-name",
            "t1bot",
        ],
    )

    colck_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    rviz_node = Node(
        package="rviz2", executable="rviz2", arguments=["-d", defaule_rviz_config_path]
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            os.path.join(pkgpath, "config", "velocity_control.yaml"),
        ],
        output="both",
    )

    controller_spawner_node = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["velocity_controller", "joint_state_broadcaster"],
    )

    return LaunchDescription(
        [
            robot_state_publisher_node,
            rviz_node,
            # ros2_control_node,
            controller_spawner_node,
            gazebo_node,
            addrobot_node,
            colck_node,
        ]
    )
