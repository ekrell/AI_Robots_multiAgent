## 1. Project description

### 1.1 Purpose.

Users of unmanned surface vehicles (USVs), such as first responders in a marine mass casualty search and rescue scenario, 
can better control the vehicles with an overhead view. As the USVs increase distance from the operators, 
the depth perceptual makes it difficult to discern the situation. More effective decisions can made using the improved
situation awareness from an overhead view. It has been demonstrated in [Xiao] that a quadcopter Unmanned Aerial Vehicle (UAV) visually tracking the 
USVs can provide an effective elevation for improved decision making and situation awareness. This page aims to demonstrate that
using communication, rather than image processing, can support path prediction to better keep the targets in the field of view. 
The target robot system that is a group of EMILYs (USVs) and a DJi Phantom (UAV). The project will be demonstrated in the Morse simulator, 
but with easy transfer to hardware in mind. It could either be implemented as a script for a ground control station (GCS), 
such as Mission Planner, or in a companion computer attached to a UAV.  

### 1.2 Implementation Overview.

The project is focused around a core Follow_USVs behavior that keeps the USVs in view by following the centroid of the USVs,
but periodically adjusting the standoff distance and camera tilt to keep the entire group in camera view. The algorithm makes the
assumption that the USVs are traveling and working as a group and thus are close enough to each other that "following" the group is feasible. 
Widely dispersed USVs would be better monitored by a behavior that cyclically visits each subgroup, as demonstrated in [--]. 
Follow_USVs would be a good fit for a system where a specific tracking behavior is selected depending on mission characteristics and
spread of the USVs. Rather than extend a single existing algorithm, Follow_USVs takes inspiration from three main sources, as will be discussed. 

The Follow_USVs behavior is based around predicting and following the path of the USV group's centroid.
The concept of focusing on the centroid was described in [--]. 
The UAV is listening for periodic updates of position and trajectory (waypoints) that are broadcast by the USVs. 
This information can be used to model the speed of the centroid and construct a set of waypoints that corresponds to the 
centroid's predicted trajectory. By following this path, the UAV's camera captures ahead of the overall group direction.
This can help first responders see where the USVs are going and help better guide them. 

Determining the standoff distance from the centroid is critical to keeping the USVs in view and promoting quality imagery. 
When the USVs are close together, the standoff distance can be reduced and the UAV can capture closer imagery and a less distorted perspective. 
However, when the USVs are further apart, the distance must increase and the camera tilt upward to maintain coverage.
This component of the algorithm will borrow from [--], which demonstrated choosing an appropriate distance based on sensor angle,
overall speed of targets, target spread and error margins.  

The predicted path can also reduce the amount of UAV movements in order to reduce the energy consumption. 
Instead of constantly repositioning the UAV based on the current state of the USVs, the UAV can 
select a position that is expected to keep the USVs in view for some duration. 
While the UAV is in position, it can continue to track the USVs by tilting the camera. 
	
The actual task of following the centroid is performed by setting waypoints and adjusting the speed of the UAV to maintain
a target standoff distance. If the UAV's distance from the centroid is less than the target standoff distance, then the UAV reverses
with speed proportional to its distance from the standoff distance. If the UAV is further than the standoff distance, it speeds toward
the standoff distance, proportional to the distance. In either case, the speed is limited by a maximum speed parameter. 

By making use of USV trajectories, the UAV will be able to plan ahead for smoother behavior. 
For example, if the USVs reach their destination and begin tending to victims, the UAV will be expecting this
and will not fly off because it has not yet obtained a position notification that tells it the USVs are now behind. 
The UAV should slow down and halt, while keeping the USVs in view. To deal with disparities between predicted and actual USV locations, 
an extended Kalman filter should be applied to construct a more accurate prediction over time. 

The ability to plan ahead also impacts the amount of network communication required for stable operation. 
In order to keep bandwidth usage low, it was decided that the UAV should not send messages to the USVs. 
While two-way communication could potentially aid path planning, 
this approach makes less system requirements (portability) while reducing the network traffic. Waypoints should be sent
less often than position updates, but waypoints  still require periodic retransmission since no handshaking ensures that 
anything was listening when the waypoint was initially announced. This applies more to the case where a companion computer is 
onboard the UAV and USVs transmit directly to the UAV. For the case where the system takes place as GCS scripts, the 
consideration of lost waypoint messages is less significant. 

In order to not interfere with other possible constraints such as FAA regulations or less variables impacting the imagery, 
Follow_USVs does not modify the UAV altitude. However, other components could be in place to alter the altitude based on flags output by
Follow_USVs. 

### 1.3 Programming Language.

The Python language was chosen because it is well suited for working with the Morse simulator and is supported in 
Mission Planner GCS. Morse is very flexible simulation environment that is rendered in a 3D Blender world.
Prototyping is well supported as the Morse system allows the creating of customized robots by selecting a base platform and
adding sensors and actuators such as "RGB Camera", "Pose", and "Waypoint". Aqueous environments are not readily available, so
UGVs are being used as as analogue. Environmental factors such as wind and waves impact the path of USVs. These factors are not
explicitly modeled in simulation, but an error margin will be used to represent uncertainty when considering whether a UGV is in view. 

### 1.4 Equipment.

#### 1.4.1 Equipment for Development.

Because of the number of robots required, the project is being done entirely in simulation (for now). 
The team members will be using their personal computers for development. 
The required development tools are the Morse simulator, python3 and Git for version control. 

#### 1.4.1 Equipment for Execution.

The Morse simulator and Python3 are required in order to execute the simulation. 
The hardware port could be done in a number of ways, but at minimum would require multiple EMILYs and a DJi Phantom. 
Since the project is heavily based around prediction using the USV's waypoints, smart EMILYs are needed. 
Technically, a single EMILY could be used it simply would not demonstrate the full extent of the algorithm. 

## 2. Inputs

The algorithm depends on certain states and parameters of the UAV as well as periodic updates on the positions and trajectories of the target USVs. 
It is expected that the UAV's current position, altitude, and speed are accessible either through Mission Planner or as a direct transmission
between the vehicles. In simulation, these fields are provided through the Morse environment. 
The maximum speed is a parameter to the algorithm; it should be able to be explicitly
input by the user (or another system component) so that the robot's actual limit can be restricted. 
When simulating the messages broadcast from the USVs, periodic transmissions will be enforced even t
hough the UAV could "cheat" and check the values straight from the simulator environment. 

## 3. Outputs

### 3.1 Outputs. 

Follow_USVs should periodically update a local file on the GCS with the system state. Logging each state as a row of a CSV
would facilitate diagnosis and testing by plotting appropriate fields. Other system components, such as other scripts being run in Mission Planner
could use this information. For example, Follow_USVs does not modify the altitude, but a helper function could see that field of view is 
reaching its limit and choose the raise the altitude. While not an output of the algorithm itself, 
the project is built around the transmission of imagery from the onboard camera. 

### 3.2 Interfaces and Mockups

!!!!!!! Need to put something here

## 4. Use case(s)

The capsized vessel has come into view and number of people can be seen struggling to hold onto its rapidly sinking hull. 
Others are nearby on floating cargo and other structures. The first responders on board are able to deploy the EMILYs, but
are far enough that their view is at a low angle. Also, some parts of the disaster scene are occluded by the floating structures. 
The team decides to send out a group of EMILYs, but also have the quadcopter follow them so they can better assess the situation.
While the EMILYs are being let out into the water, the quadcopter operator opens his laptop and arms the vehicle. 
Mission Planner is already running and the operator selects the Follow_EMILYs script. 
The maximum speed is set from a previously setup configuration file, and the operator is prompted to select which EMILYs are 
part of the target group. The operator hits 0 as code for 'all' and the quadcopter arms, raises above the ground and accelerates 
toward its first calculated waypoint. The EMILYs begin making their way toward the victims and the quadcopter periodically repositions
to maintain them in the field of view. The first responders can watch the EMILYs travel to the site and since the quadcopter is following from
behind and looking ahead, they have a much better sense of the disaster scenario. Better informed, the team selects new waypoints to 
aid those most in dire need of assistance. All the while, the quadcopter provides a view with clear depth perception and no significant occlusions. 


[ Another case where the group splits off. UAV continues to follow the "main" group, but sends a notification that one of the EMILYs 
has strayed from the group and it outside coverage. ]


	
## 5. Test Plan

The goal is to determine if the quadcopter will be able to constantly keep a group of USVs within camera
view by following the group through repositioning and camera tilting, using position and trajectory messages broadcast by the USVs. 
The hypothesis is that the trajectory messages will allow the UAV to make effective path predictions that maintain 
camera coverage using less movements than if only current positions were communicated. Using less movements is important because
it conserves energy and thus increases the available flight time. Also, less movements would result in a stabler image which 
reduces the disorienting effect of a shakey image, and potential image processing applications would benefit from the improved image quality. 

The algorithm will be tested in the Morse simulator, using a single quadcopter and variable number of ground vehicles. 
The quadcopter will have a speed actuator and an abstract 'Waypoint' actuator. The ground vehicles will also have speed and waypoint control. 
Both robot types will have a Pose sensor for localization, and the quadcopter will have an RGB camera with tilt control. 

A constant starting location will be set as the "base", as if this is the ship or shore from which the USVs are deployed. 
Each run has a specific USV message broadcast rate for the current position and trajectory messages.
The UGVs will be initialized from this location, but 3 meters apart from each other and base.
Each UGV will loaded with a set of waypoints. Each set will conclude with a waypoint to the "home" position for pickup. 
The waypoints will be selected to be within 200 yards from the base, based on the expected maximum distance between base and victims. 
Also, the UGVs are assumed to be working as a group and stay within some distance. The waypoints will be assigned such that the
UGVs do not leave the maximum camera footprint, given the constant altitude. 
The UGVs are sent off and then the UAV is as well. 
The experiment will run until all vehicles have returned within 3 meter of the base for pickup or until the expected mission duration has gone overtime by 5 minutes. 
Expected mission duration is calculated based on the total distance from each waypoint and the USV speeds. 

The dependent variables of interest are the percentage of total time that all the USVs are kept in view 
and the amount of time that the UAV spends adjusting its position. 
The main independent variables are the position and trajectory message broadcast rates which relates the hypotheses. 
Other independent variables are the random start positions, trajectories and speeds in order to avoid a scenario that happens to be biased.
To get meaningful results despite several independent variables, runs consist of two levels for combinatorial experiments. 
At level one, the UGV path is set, which varies the waypoints, speeds, and group size. 
Within that, level two controls the message broadcast rates. Thus, the UGV path is held constant for each set of message broadcast experiments. 

