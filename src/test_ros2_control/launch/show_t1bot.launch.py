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
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource
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

    urdfname = get_package_share_directory("test_ros2_control")
    t1bot_desc = os.path.join(urdfname, "urdf", "t1bot.xacro")
    defaule_rviz_config_path = os.path.join(urdfname, "config", "show_model.rviz")

    # 节点 A：robot_state_publisher (核心！)
    # 作用：自动读取并解析 xacro 文件，向全网发布 /robot_description 和 TF 坐标树
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                # 使用 Command 动态调用 xacro 命令解析文件
                "robot_description": Command(["xacro ", t1bot_desc])
            }
        ],
    )

    # 节点 B：joint_state_publisher_gui
    # 作用：弹出一个带滑块的 GUI 窗口，发布非固定关节（如 revolute）的角度
    # 注意：如果不启动它，RViz2 会报 No transform from [link1] to [base_link]
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
    )

    rviz_node = Node(
        package="rviz2", executable="rviz2", arguments=["-d", defaule_rviz_config_path]
    )

    return LaunchDescription(
        [
            robot_state_publisher_node,
            joint_state_publisher_gui_node,
            rviz_node,
        ]
    )
