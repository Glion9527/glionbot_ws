import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer
from tf_transformations import euler_from_quaternion


class TFListenerPy(Node):
    def __init__(self):
        super().__init__("tf2_listener_py")
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.timer = self.create_timer(1, self.get_transform)

    def get_transform(self):
        try:
            tf = self.buffer.lookup_transform(
                "map",
                "base_footprint",
                rclpy.time.Time(seconds=0),
                rclpy.time.Duration(seconds=1),
            )
            transform = tf.transform
            rotation_euler = euler_from_quaternion(
                [
                    transform.rotation.x,
                    transform.rotation.y,
                    transform.rotation.z,
                    transform.rotation.w,
                ]
            )
            self.get_logger().info(
                f"平移：{transform.translation}, 旋转四元数：{transform.rotation},旋转欧拉角：{rotation_euler}"
            )
        except Exception as e:
            self.get_logger().warn(f"不能获取坐标变换，原因：{str(e)}")


def main():
    # 2、初始化ROS2客户端
    rclpy.init()
    # 4、调用spin函数，并传入节点对象指针
    rclpy.spin(TFListenerPy())
    # 5、释放资源
    rclpy.shutdown()


if __name__ == "__main__":
    main()
