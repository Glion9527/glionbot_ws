#include "glionbot_application_cpp/tf_listener.hpp"
#include <cmath>
// 3、自定义节点类
TFListener::TFListener() : Node("tf2_listener_cpp")
{
  // 创建TF缓冲区
  buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
  // 创建TF监听器
  listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_);
  // 创建定时器，每秒调用一次
  timer_ = this->create_wall_timer(
      std::chrono::seconds(1),
      std::bind(&TFListener::get_transform, this));
}

TFListener::~TFListener() {}

void TFListener::get_transform()
{
  try
  {
    // 查找坐标变换
    geometry_msgs::msg::TransformStamped tf = buffer_->lookupTransform(
        "map",
        "base_footprint",
        rclcpp::Time(0),
        rclcpp::Duration::from_seconds(1.0));

    // 获取平移信息
    auto translation = tf.transform.translation;
    // 获取旋转四元数
    auto rotation = tf.transform.rotation;
    // 将四元数转换为欧拉角
    tf2::Quaternion quat(
        rotation.x,
        rotation.y,
        rotation.z,
        rotation.w);

    tf2::Matrix3x3 mat(quat);
    double roll, pitch, yaw;
    mat.getRPY(roll, pitch, yaw);

    RCLCPP_INFO(this->get_logger(),
                "平移：[%.3f, %.3f, %.3f]"
                "旋转四元数：[%.3f, %.3f, %.3f, %.3f]"
                "旋转欧拉角：[%.3f, %.3f, %.3f]",
                translation.x, translation.y, translation.z,
                rotation.x, rotation.y, rotation.z, rotation.w,
                roll, pitch, yaw);
  }
  catch (const std::exception &e)
  {
    RCLCPP_WARN(this->get_logger(),"不能获取坐标变换，原因 : %s",e.what());
  }
}

int main(int argc, char const *argv[])
{
  // 2、初始化ROS2客户端
  rclcpp::init(argc, argv);
  // 4、调用spain函数，并传入节点对象指针
  rclcpp::spin(std::make_shared<TFListener>());
  // 5、释放资源
  rclcpp::shutdown();
  return 0;
}