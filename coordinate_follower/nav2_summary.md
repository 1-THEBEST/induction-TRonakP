# Nav2 Workflow Summary

### NavigateToPose Goal Lifecycle
When our mission client sends a coordinate goal to `MapsToPose`, the **Behavior Tree Navigator** takes it first. The BT Navigator checks its XML tree to decide what to do next. It calls the **Planner Server** to calculate a clean path from where the rover is standing to the destination. Once that path is ready, the BT Navigator forwards it to the **Controller Server**. The controller then breaks this path down into real-time velocity commands (`cmd_vel`), steering the motors while constantly checking for any obstacles.

### Global vs. Local Costmaps
* **Global Costmap:** This builds a map of the entire environment. The **Planner Server** uses it to figure out a long-distance route to the goal. This can only be done by looking at the big map at once.
* **Local Costmap:** This is a small, moving window centered right on the rover. The **Controller Server** uses it to process live LiDAR data to dodge obstacles while moving.

We need two different costmaps because calculating a long-distance path requires looking at the whole map at once, while dodging immediate obstacles needs a fast and lightweight loop. Updating a massive map with high-frequency LiDAR data would completely overwhelm the on-board computer.
