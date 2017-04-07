## 1. Project description

### 1.1 Purpose.

First responders in a search and rescue scenario can better make use of USVs, such as EMILYs, with close overhead imagery of the USVs and their surroundings. 
As the USVs increase distance from the first responders, the view from the boat or shore lacks the desired depth perception and is partially occluded by the USVs. 
This project aims to provide first responders with an improved view of the USVs by following their group with a UAV and maintaining the vehicles in the field
of view of the UAV's camera. In addition to streaming the imagery to the first responders, this project could be extended upon by using that imagery for
image processing tasks to improve the sensory capability of the USVs. For example, the UAV could detect obstacles and notify the USVs. 
The project will be implemented as a script for a ground control station (GCS) software that controls a quadcopter. 

### 1.2 Implementation Overview.

The project is focused around a core Follow_USVs behavior that keeps the USVs in view by following the centroid of the USVs,
but contanstly adjusting the standoff distance and camera tilt to keep the entire group in camera view. The algorithm makes the
assumption that the USVs are traveling and working as a group and thus are close enough to each other that "following" the group is feasable. 
Widely dispered USVs would be better monitored by a behavior that cyclicly visits each subgroup, as demonstrated in [--]. Ideally, such a 
behavior could be selected instead when appropriate. 
The algorithm is not building off a single existing system, but rather takes inspiration from three main sources. 

The Follow_USVs behavior is based around predicting and following the path of the USV group's centroid.
The concept of focusing on the centroid was described in [--]. 
The UAV is listening for periodic updates of position and trajectory (waypoints) that are broadcast by the USVs. 
This information can be used to model the speed of the centroid and construct a set of waypoints that corrospond to the 
centroid's predicted trajectory. By following this path, the UAV's camera captures ahead of the overall group direction.
This can help first responders see where the USVs are going and help better guide them. 

Determining the standoff distance from the centroid is critical to keeping the USVs in view and promoting quality imagery. 
When the USVs are close together, the standoff distance can be reduced and the UAV can capture closer imagery and a less distorted perspective. 
However, when the USVs are further apart, the distance must increase and the camera tilt upward to maintain coverage.
This component of the algorithm will borrow from [--], which demonstrated choosing an appropriate distance based on sensor angle,
overall speed of targets, target spread and error margins.  
	
The actual task of following the centroid is performed by setting waypoints and adjusting the speed of the UAV to maintain
a steady standoff distance. The speed adjustment is done through a simple piecewise function that slows the UAV with greater magnitude as
the UAV is within the distance and increases the speed when the outside, up to some maximum speed. Near the standoff distance, the
speed adjustment is infantesimal for maintaining an equillibrium speed. 

		UAV.SPEED = [ (TARGET_DIST - CURRENT_DIST) / (TARGET_DIST) ] (UAV.SPEED)    if CURRENT_DIST < TARGET_DIST
		UAV.SPEED = UAV.SPEED                                                       if CURRENT_DIST == TARGET_DIST
		UAV.SPEED = [ (TARGET_DIST + CURRENT_DIST) / (TARGET_DIST) ] (UAV.SPEED)    if CURRENT_DIST > TARGET_DIST


By making use of USV trajectories, the UAV will be able to plan ahead for smoother behavior. 
For example, if the USVs reach their destination and begin tending to victims, the UAV will be expecting this
and will not fly off because it has not yet obtained a position notification that tells it the USVs are now behind. 
The UAV should slow down and halt, while keeping the USVs in view. To deal with disparities between predicted and actual USV locations, 
an extended Kalman filter should be applied to construct a more accurate prediction over time. 

The ability to plan ahead also impacts the amount of network communication required for stable operation. 
In order to keep bandwidth usage low, it was decidedthat the UAV should not send messages to the USVs. 
While two-way communication could potentially aid path planning, 
this approach makes less system requirments (portability) while reducing the network traffic. Waypoints should be sent
less often than postion updates, but still require periodic retransmission since no handshaking ensures that 
anything was listening when the waypoint was initially announced.

In order to not interefere with other possible constraints such as FAA regulations or less variables impacting the imagery, 
Follow_USVs does not modify the UAV altitude. However, other systems could be in place to alter the alitude based on flags output by
Follow_USVs. 

### 1.3 Programming Language.

The Python language was chosen because it is well suited for working with the Morse simulator and it supported in 
Mission Planner GCS. Morse is very flexable simulation environment that is rendered in a 3D Blender world.
Prototyping is well supported as the Morse system allows the creationg of customized robots by selecting a base platform and
adding sensors and actuators such as "RGB Camera", "Pose", and "Waypoint". Aqueous environments are not readily available, but 
UGVs are being used as a suitable analogue. 

### 1.4 Equipment.

#### 1.4.1 Equipment for Development.

Because of the number of robots required, the project is being done entirely in simulation. 
Thus, the personal computers of the team members are all that is required. However, since the ultimate goal is 
actual implementation on the robots, the goal is to facilitate a smooth transition from simulation to robots. 

#### 1.4.1 Equipment for Execution.

Same as for development. 

## 2. Inputs

The algorithm depends on certain states and parameters of the UAV as well as periodic updates on the positions and trajectories of the USVs. 
It is expected that the UAV's current position, altitude, and speed are accessable through Mission Planner. In simulation, these fields are 
provided through the Morse environment. The minimum and maximum speeds are parameters to the algorithm. They should be able to be explicelty
input by the user (or another system component) so that the robot's actual limits can be restricted. When simulating the messages broadcast from
the USVs, delays will be programmed even though the UAV could "cheat" and check the values directly.

## 3. Outputs

### 3.1 Outputs. 

Follow-USVs should periodically update a local file on the GCS with the system state. Logging each state as a row of a CSV
would facilitate diagnosis and testing by plotting appropriate fields. Other system components, such as other scripts being run in Mission Planner
could use this information. For example, Follow-USVs does not modify the altitude, but a helper function could see that field of view is 
reaching its limit and choose the raise the altitude. [Should we mention the camera output? Indirectly part of algorithm]. 

### 3.2 Interfaces and Mockups

[Intended to be used within a larger system with a UI. What is expected here?]

## 4. Use case(s)

- EMILYs are launched from boat and sent to target area with victims. 
	
## 5. Test Plan

Since in simulation, can do a large number of runs with a variety of configurations
Particularly interested in the boundaries. When are USVs too far apart to keep all in view, simultaneous.
When should a "Visit-USVs" behavior be more appropriate? Also, what is the minimum broadcast rate support 
effective UAV Following. 

_metrics_

- % time all kept in view
- % USVs kept in view
- Bandwidth usage / number of messages
- UAV smoothness
- Image stability

_experimental parameters_

- Number of USVs
- USV speeds
- USV paths
- USV spatial distribution
- Broadcast message rate




