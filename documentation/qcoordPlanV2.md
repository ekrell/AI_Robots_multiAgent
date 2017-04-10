## QCOORD: Track multiple surface vehicles

This document contains ideas for implementing a system that allows a single UAV (named QCOORD) 
to constantly reposition itself to keep multiple surface vehicles (TARGETS) in view. 

### Goals: 

- Primary goal: keep TARGETS in camera field of view (FOV)
- Minimize Communication: bandwidth considerations
- Improve sensory awareness for TARGETS: promote stable imagery and attempt to look "ahead" of TARGETS
- [Requires verification] When TARGETS are beyond maximum FOV, continually visit each subgroup
- Address contention: keep TARGETS in view even when QCOORD asked to image other subjects. 



### Assumptions:

TARGET capabilities:

The TARGETS broadcast their position and trajectory. 
This means that not only do they share their position at a given time, but also a set of their next waypoints. 
However, they do not share their speed or any other information. 
TARGETS are either 'working' or 'traveling'. 
When traveling, it is assumed that the TARGETS are headed in the same general direction such that
it makes sense to have a concept of "following" the group. 
At various points, the TARGETS are working. An example would be if they reach their destination and 
are helping victims in a search and rescue scenario. They are expected to be working within
a close enough vicinity that QCOORD can continue to keep them in view until they begin traveling. 

QCOORD is a quadcopter with a camera that is able to tilt, but not pan. 
It is able to listen for messages broadcast from the TARGETS, but does not send any messages to the TARGETS. 
As a Quadcopter, QCOORD is able to hover and change speed more easily than a fixed wing. 
Thus, its movement can be abstracted to resemble that of a surface vehicle at a given altitude. 

While the primary goal is to always keep the TARGETS in FOV, there is a physical limit to
how spread apart TARGETS and maitain constant FOV.
In the case that the TARGETS are too dispersed for the follow behavior, 
some other action must take place.
Proposed solutions include: follow larger subgroup, ask for operator instructions, or switch to an
alternative tracking mode that cyclicly visits each subgroup. 
The follow behavior, also called core tracking algorithm, would not try to take on these
duties, but instead produce an output flag so that another component can decide what course of action
to take. The component could be based around predefined user parameters, select based on a rule set, 
or make a deliberative decision. 

### Core Tracking Algorithm:

**Definitions**

- N = number of TARGETS (also written as |TARGETS|)
- Formation = the positions of the TARGETS as a whole at a given time 
- X = centroid of Formation
- FOV = Area of surface visible in camera image
- InFOV(x) = { TRUE if every member of x is within FOV, FALSE otherwise }
- TARGETS[i].Position = (X, Y) coordinates of ith TARGET 
- TARGETS[i].Trajectory = ordered set of future waypoints for ith TARGET
- X.Position = Centroid's (X, Y) coordinates
- X.Trajectory = Centroid's set of predicted waypoints
- R = Standoff distance from X

**Focus Statement**

The focus of this document is on the core algorithm for keeping TARGETS in FOV. 
Also described is how it would interact with a larger system, 
including various constraints that could be set or relaxed to modify the behavior. 
Ideally, the core algorithm is simple enough to handle a variety of situations with largely reactive behaviors. 
This algorithm purposefully does not make use of every aspect of the vehicles capabilities. 
In order to support more situations, the algorithm was allowed to have tighter bounds allowable Formations.
For example, because of FAA restrictions or potential use case requirements, the altitude is assumed to be constant. 
This means that QCOORD cannot simply raise its altitude when the spread of TARGETS is too far apart,
but nothing is stopping other system components from autonomously adjusting the altitude.

**Basic Descriptio**n

The core algorithm works by following the centroid X while maintaining a speed, distance, and camera tilt angle
that ensures InFOV(TARGETS) is TRUE.
QCOORD uses the trajectory of the TARGETS to predict the trajectory of the centroid. 
QCOORD also uses the position of the centroid to slow down or speed up such that it 
should maintain an equilibrium standoff distance R. 
In order to maintain a smoother path, an extended Kalman filter (or something similar) could be applied.


**Considerations**

_Follow Behind_

The purpose of such a system is to support sensory awareness. 
This could be having QCOORD use image processing to aid the TARGETS with obstacle avoidance.
Or, it could be to help human supervisors get a better idea of where the TARGETS are headed. 
Thus, we deemed it appropriate to follow the TARGETS from behind and focus imagery on what is ahead. 

_Centroid Approach_

Individual TARGETS could be very "stop and go" in their movement, or spend some time doing non-holonomic turning. 
A simple way to consider following the group as a whole was the follow their centroid X. 

_Change Speed_

Unlike much of the literature, which uses fixed-wing UAVs, QCOORD can change speed. 
We are using a simple piecewise function that dynamically adjusts the speed based on the distance
from an observed centroid. The further out from R, speeds up to catch up. If QCOORD is within R, needs to slow down. 
The slow and speed up is negligible near R, so stays at R and the motion should be too jerky if the centroid's speed
is stable. 

_Standoff Distance_

The standoff distance, R, is the distance to keep behind the centroid such that InFOV(TARGETS) = True. 
FOV is based on altitude and tilt angle. 

_Tilt Angle_

The tilt angle changes the dimensions of the FOV.
This angle should be dynamically readjusted to grow or shrink the FOV. 
The FOV should be narrow to get a better view of the TARGETS when their Formation is tighter, 
and FOV should enlarge when the Formation is spread apart to keep in view. 

_Path_

Use the trajectories of the TARGETS and the estimated centroid speed to plan a path.
By having such a path, QCOORD has something to follow without constant position updates from the TARGETS. 
This should be especially useful when the TARGETS are in a 'working' phase, 
since QCOORD will know not the just "fly off" in whatever direction it was going since last update. 

_Path Smoothing_

Since their may be discrepancies between the predicted path and the observed centroid positions, 
could use something like a Kalman filter to continually refine the path based on observations. 
We do not yet know enough about such filters to recommend the appropriate technique with certainty.

_Communication_

We chose to not have QCOORD talk to the TARGETS. 
This may sacrifice potential gains in performance, but feels most appropriate since it
lessens capability requirements for the TARGETS, makes room for other kinds of potential communication
such as obstacle warnings, and lowers the bandwidth requirements. 
In addition, there will be separate messages for positions and trajectory waypoints. 
Waypoints can be sent less often than positions, but should be broadcast periodically since
there is no handshaking to ensure that anyone was listening when it was sent. 


### Overall System Overview:

Section is a work in progress. 
Should talk about how communication is handled, 
how algorithm organized, 
how separate duties such as altitude is handled by read by the algorithm.
Should consider how the algorithm could work with other "layers",
or how this behavior could be subsumed by other layers that do other tasks while keeping the Follow in mind. 

**Layers**

The core tracking algorithm is a behavior within a larger context. 
A number of parameters control the behavior, but the behavior should not be forced 
to restart to use a modified parameter. In this way, the behavior can be dynamically
be adjusted from the "outside" when another component modifies, for example, the altitude.

The following information should be accessible by the algorithm:

- Maximum speed - internat state
- Minimum speed (default is 0 -> halted) - internal state
- Altitude - internal state
- Camera specifications for tilt range and FOV - internal state
- Most recent position of each TARGET - via logical sensor
- Trajectory of each TARGET - via logical sensor

The last two are updated as QCOORD received messages broadcast from the TARGETS. 
Thus, a listening component is mandatory for QCOORD. 
Will be further described in the Communication section.
Logical sensors are used because it should not matter to the algorithm where
the positions and trajectories came from. 
One could even model non-vehicles as 'TARGETS' if they are to be followed as well. 
In this way, drowning victims could be considered stationary targets and affect the centroid path. 

The algorithm itself can be divided into distinct phases:

- Construct/update centroid path prediction -> set of waypoints
- Determine standoff distance that keeps TARGETS in view
- Send next waypoint to the Waypoint actuator
- Adjust speed based on relation to centroid
- Report status/diagnostic info
- Spend some time traveling before recomputing and correction

Components that "surround" the algorithm:

- Selector the turns behavior on or off
- Target selection, determine what are the TARGETS
- Communication layer that (minimally) listens for messages from TARGETS
- Subsuming behavior that builds off of the follow algorithm, but could perform additional maneuvers or relax constraints. 
- [Requires Verification] Another algorithm "beside" Follow that implements visiting each subgroup, not simultaneously.  


**Communication**

QCOORD does not send any messages the TARGETS.
It must be constantly listening for messages broadcast by the TARGETS. 
These messages populate the values behind logical sensors that contain each 
of the TARGETS last received position and trajectory (set of waypoints).

In order to minimize network usage, two message types exist that are sent at different intervals.

- Current position (more frequently)
- Future waypoints (less frequently) -> Used to construct trajectory

QCOORD does not mandate an update rate, but will not effectively keep TARGETS in view if rate is too slow. 
A good update rate is fast enough for QCOORD to maintain a stable Follow behavior, but without being needlessly noise. 
Ideally the TARGETS could adjust their rates depending on their speed or degree of path variability. 
Recommended default rates will be determined through testing. 


### Testing:

Testing will be performed to gauge whether the system is effective in keeping the TARGETS in view for a number of scenarios. 
Some test cases will be focused on approximating realistic use cases, but others will be to find limitations. 

**Environment**

The "class project" phase will be tested entirely in simulation. 
The Morse simulator was chosen for its ease of setting up diverse robots with custom sensors and actuators. 
A 3D blender world is used to view the actions of the robots in 3D space, which makes it easy to visualize exactly what 
the robots are going to do. 

**Metrics**

The metrics will be measured using a variety of parameters (altitude, max & min speed, etc)
and using a variety of scenarios (number of TARGETS, their spread, speeds, trajectories, etc)

- How much time are the TARGETS actually in FOV? - MAX
- How much bandwidth is being used? - MIN
- How "Jerky" is QCOORD's path - MIN
- How far apart can TARGETS be and still support Following? MAX
- How stable is camera imagery? MAX














