import os
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class MissionClient(Node):
    def __init__(self):
        super().__init__('mission_client')
        
        # Declare ROS parameter for the waypoint file path
        self.declare_parameter('waypoint_file', 'waypoints.txt')
        waypoint_file_param = self.get_parameter('waypoint_file').value
        
        # Initialize metrics and tracking
        self.waypoints = self.load_waypoints(waypoint_file_param)
        self.total_waypoints = len(self.waypoints)
        self.current_index = 0
        self.successful_goals = 0
        
        # Create Action Client for Nav2 NavigateToPose
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
        if self.total_waypoints == 0:
            self.get_logger().error("No valid waypoints loaded. Shutting down node.")
            self.destroy_node()
            return

        self.get_logger().info(f'Loaded {self.total_waypoints} waypoints from {waypoint_file_param}')
        
        # Wait for the action server to be available before starting execution
        self.get_logger().info('Waiting for Nav2 action server...')
        self._action_client.wait_for_server()
        
        # Begin the sequential dispatch chain
        self.send_next_waypoint()

    def load_waypoints(self, file_path):
        """Reads space-separated x y coordinates from a text file."""
        waypoints = []
        if not os.path.isabs(file_path):
            # Fallback to local directory if relative path provided
            file_path = os.path.join(os.getcwd(), file_path)
            
        if not os.path.exists(file_path):
            self.get_logger().error(f"Waypoint file not found at: {file_path}")
            return waypoints

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    # Skip empty lines or commented lines
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            x = float(parts[0])
                            y = float(parts[1])
                            waypoints.append((x, y))
                        except ValueError:
                            self.get_logger().warn(f"Skipping malformed line: '{line}'")
        except Exception as e:
            self.get_logger().error(f"Failed to read waypoint file: {str(e)}")
            
        return waypoints

    def send_next_waypoint(self):
        """Dispatches the next waypoint asynchronously, or ends the mission."""
        if self.current_index >= self.total_waypoints:
            self.get_logger().info(
                f'Mission complete: {self.successful_goals}/{self.total_waypoints} waypoints reached'
            )
            # Gracefully spin down the node after layout completion
            return

        x, y = self.waypoints[self.current_index]
        self.get_logger().info(
            f'Dispatching waypoint {self.current_index + 1}/{self.total_waypoints}: x={x:.2f}, y={y:.2f}'
        )

        # Construct NavigateToPose goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        # Position
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        
        # Orientation (Facing forward relative to frame; maintaining neutral quaternion)
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        # Async dispatch with continuous feedback tracking
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        """Prints live remaining distance metrics to the terminal."""
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: distance remaining = {feedback.distance_remaining:.2f} m')

    def goal_response_callback(self, future):
        """Handles server response confirming if goal was accepted."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn(f'Waypoint {self.current_index + 1} was REJECTED by server.')
            # Skip to next waypoint if current one falls through
            self.current_index += 1
            self.send_next_waypoint()
            return

        # Fetch result asynchronously if goal accepted
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Processes execution outcomes and routes to the next waypoint."""
        result = future.result()
        status = result.status
        
        # Check standard Nav2 execution statuses (SUCCEEDED == 4)
        if status == 4:
            self.get_logger().info(f'Waypoint {self.current_index + 1} SUCCEEDED')
            self.successful_goals += 1
        else:
            self.get_logger().warn(f'Waypoint {self.current_index + 1} FAILED or ABORTED with status code: {status}')

        # Move to next index and recurse back into pipeline loop
        self.current_index += 1
        self.send_next_waypoint()

def main(args=None):
    rclpy.init(args=args)
    node = MissionClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
