import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleController(Node):
    def __init__(self):
        # Initialize the node with a name
        super().__init__('turtle_controller_node')
        
        # Create a publisher for the cmd_vel topic
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Create a timer to publish at 10 Hz (0.1 seconds)
        timer_period = 0.1  
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # Create a Twist message
        msg = Twist()
        
        # Set the linear and angular velocities
        msg.linear.x = 0.2
        msg.angular.z = 0.5
        
        # Publish the message
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: linear x: %f, angular z: %f' % (msg.linear.x, msg.angular.z))

def main(args=None):
    rclpy.init(args=args)
    turtle_controller = TurtleController()
    
    try:
        rclpy.spin(turtle_controller)
    except KeyboardInterrupt:
        pass
    finally:
        turtle_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()