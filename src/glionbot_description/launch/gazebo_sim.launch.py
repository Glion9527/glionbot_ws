from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

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
    world_file = "turtlebot3_house.world"
    robot_name_in_model = "glionbot"
    urdf_tutorial_path = get_package_share_directory("glionbot_description")
    default_model_path = os.path.join(
        urdf_tutorial_path, "urdf", "glionbot", "glionbot.urdf.xacro"
    )
    default_world_path = os.path.join(
        urdf_tutorial_path, "world", world_file
    )
    # 为launch声明参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model",
        default_value=str(default_model_path),
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
        parameters=[
            {"robot_description": robot_description},
            # {"use_sim_time": True},
        ],
    )

    # 1. 通过 IncludeLaunchDescription 包含 Gazebo Harmonic 的启动文件
    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [get_package_share_directory("ros_gz_sim"), "/launch", "/gz_sim.launch.py"]
        ),
        # Gazebo Harmonic 使用 gz_args 来传递参数
        # -r 表示启动后直接运行（不暂停）
        # -v 4 表示输出详细的 verbose 级别日志
        launch_arguments={"gz_args": ["-r ", default_world_path]}.items(),
    )

    # 2. 请求 Gazebo Harmonic 加载机器人
    spawn_entity_node = Node(
        package="ros_gz_sim",
        executable="create",  # 在 Harmonic 中，加载实体的可执行文件名为 create
        arguments=[
            "-topic",
            "/robot_description",
            "-name",
            robot_name_in_model,
            "-x",
            "-4.0",
            "-y",
            "4.0",
            "-z",
            "0.0",
        ],
        output="screen",
    )

    camera_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image", "/camera/depth_image"],  # 彩色图像  # 深度图像
        output="screen",
    )

    # 3. 启动 ros_gz_bridge，桥接 ROS 2 和 Gazebo 之间的话题
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # 语法规则: /话题名称@ROS2_消息类型[Gazebo_消息类型  (或者 ] 表示方向)
            # 1. 桥接时钟 (Gazebo -> ROS 2) - 必不可少！让 ROS 2 节点使用仿真时间
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # 2. 桥接控制指令 (ROS 2 -> Gazebo) - 假设你的插件监听此话题
            # "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            # # 3. 桥接里程计 (Gazebo -> ROS 2)
            # "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            # 4. 桥接关节状态 (Gazebo -> ROS 2)
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
            # 5. 桥接 TF 树 (Gazebo -> ROS 2)
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            # 6. 桥接激光雷达传感器 (Gazebo -> ROS 2)
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            # 桥接点云 (如果你需要三维建图)
            "/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
            # 桥接相机内参信息 (RViz 显示图像时必须要有)
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        output="screen",
    )

    # 1. 孵化关节状态广播器
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    # 2. 孵化差速驱动控制器 (名字必须和 YAML 里写的一致)
    load_glionbot_base_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["glionbot_base_controller"],
        output="screen",
    )

    # ==================== 新增：配置启动顺序 (非常重要) ====================

    # 动作 1：监听 spawn_entity_node，等它加载完机器人并退出后，再启动状态广播器
    delay_joint_state_broadcaster_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[load_joint_state_broadcaster],
        )
    )

    # 动作 2：等状态广播器启动成功后，再启动差速驱动控制器
    delay_base_controller_after_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_glionbot_base_controller],
        )
    )

    dispaly_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("glionbot_description"),
                "launch",
                "display_robot.launch.py",
            )
        )
    )

    return LaunchDescription(
        [
            action_declare_arg_mode_path,
            robot_state_publisher_node,
            launch_gazebo,
            spawn_entity_node,
            camera_image_bridge,
            bridge_node,
            delay_joint_state_broadcaster_after_spawn,
            delay_base_controller_after_joint_state_broadcaster,
            dispaly_launch,
        ]
    )
