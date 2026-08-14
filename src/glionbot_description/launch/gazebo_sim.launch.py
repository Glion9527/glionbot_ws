from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare

# 封装终端指令相关类--------------
# from launch.actions import ExecuteProcess
# from launch.substitutions import FindExecutable
# 参数声明与获取-----------------
# from launch.actions import DeclareLaunchArgument
# from launch.substitutions import LaunchConfiguration
# 文件包含相关-------------------
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# 分组相关----------------------
# from launch_ros.actions import PushRosNamespace
# from launch.actions import GroupAction
# 事件相关----------------------
# from launch.event_handlers import OnProcessStart, OnProcessExit
# from launch.actions import ExecuteProcess, RegisterEventHandler,LogInfo
# 获取功能包下share目录路径-------
# from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # 获取默认路径
    robot_name_in_model = "glionbot"
    urdf_tutorial_path = get_package_share_directory("glionbot_description")
    defaule_model_path = os.path.join(
        urdf_tutorial_path, "urdf", "glionbot", "glionbot.urdf.xacro"
    )
    defaule_world_path = os.path.join(
        urdf_tutorial_path, "world", "turtlebot3_world.world"
    )
    # 为launch声明参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model",
        default_value=str(defaule_model_path),
        description="URDF的绝对路径",
    )
    # 获取文件内容生成新的参数
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]), value_type=str
    )

    # 状态发布节点
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    # 通过 IncludeLaunchDescription 包含另外一个launch文件
    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        launch_arguments={
            "gz_args": defaule_world_path,
            "on_exit_shutdown": "true",
        }.items(),
    )
    # 请求 Gazebo 加载机器人
    spawn_entity_node = ExecuteProcess(
        cmd=[
            "ros2",
            "run",
            "ros_gz_sim",
            "create",
            "-topic",
            "/robot_description",
            "-name",
            robot_name_in_model,
            "-x",
            "-2.0",
            "-y",
            "0.0",
            "-z",
            "0.0",
        ],
        output="screen",
    )

    # 启动 ROS-Gazebo 桥接器
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # 双向桥接 cmd_vel (ROS -> GZ)
            # "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/model/glionbot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            # 双向桥接 odom (GZ -> ROS)
            # "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/model/glionbot/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            action_declare_arg_mode_path,
            robot_state_publisher_node,
            launch_gazebo,
            spawn_entity_node,
            bridge_node,
        ]
    )
