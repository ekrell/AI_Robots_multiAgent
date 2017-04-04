## QCOORD: Track multiple surface vehicles

This document contains ideas for implementing a system that allows a single UAV (named QCOORD) 
to constantly reposition itself to keep multiple surface vehicles (TARGETS) in view. 

### Goals: 

- Primary goal: keep TARGETS in camera field of view (FOV)
- Minimize Communication: bandwidth considerations
- Improve sensory awareness for TARGETS: promote stable imagery and attempt to look "ahead" of TARGETS
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

_Communcation_

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

### Testing:

Need to describe testing strategies.
- Environment we test in
- That we want to find the boundaries where the follow behavior is no longer effective
- What metrics we will measure









