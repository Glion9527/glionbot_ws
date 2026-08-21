from launch import LaunchDescription
# 参数声明与获取-----------------
from launch.actions import DeclareLaunchArgument
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

# 获取功能包下share目录路径-------
from ament_index_python.packages import get_package_share_directory
import os

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
    urdf_tutorizl_path = get_package_share_directory("glionbot_description")
    default_model_path = os.path.join(urdf_tutorizl_path, "urdf","glionbot" ,"glionbot.urdf.xacro")
    # 为launch声明参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model", default_value=str(default_model_path)
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
    # 关节状态发布节点
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )
    defaule_rviz_config_path = os.path.join(
        urdf_tutorizl_path, "config", "rviz", "display_model.rviz"
    )
    # Rviz 节点
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=['-d', defaule_rviz_config_path]
    )

    return LaunchDescription(
        [
            # action_declare_arg_mode_path,
            # joint_state_publisher_node,
            # robot_state_publisher_node,
            rviz_node,
        ]
    )
