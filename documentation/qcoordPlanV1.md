## QCOORD: Track multiple surface vehicles

This document describes basic ideas for implementing an algorithm that allows a single UAV to constantly reposition itself to keep multiple surface vehicles in view.


### Plain English Overview

VERY MUCH a work in progress.. 

Multiple USVs are at work and their mobility is provided by a 'Waypoint' actuator. 
Each USV has a current position and a target position (next Waypoint).
A single UAV is responsible for keeping all of the USVs in camera view.
The UAV does not have to do any image analysis because the USV broadcasts its current and target position.



Goals: Maximize USVs being in camera view. Minimize communication.

Proposed architecture: A subsumption model whose layers handle various aspects of the behavior. 

*Level -1: Choose USVs:*

Relies on: USV positions, USV target positions. 

Affects: Internal data structures.

While the goal is to keep all in view, that might not be possible if sufficiently separate directions. 
Checks the geometry of USV positions, USV targets positions, and camera specifications. 
Could have parameters for the user to set thresholds. Should you give up entirely? Should you follow those that are going in general same direction? Etc. 


*Level 0: Follow USVs:*

Relies on: USV positions.

Affects: Waypoint actuator, Velocity Actuator.

UAV computes the centroid of the USVs and sets its waypoint for that centroid.
In order to follow behind at some distance X, the speed is constantly affected by distance from X. 
When UAV is outside X, the speed increases (up to MAX_SPEED) as it gets further and decreases as it gets closer. 
When UAV is inside X, the speed slows as it gets more inward. 
A simulated test already shows that it maintains a dynamic (roughly) equilibrium follow behavior for _one USV_. 
This is cool because it did so without knowing the USV's direction (USV's waypoint).


*Level 2: Maintain Camera View via altitude:*

Relies on: USV positions.

Affects: Altitude (via z-coord in Waypoint actuator??)

Use geometry to ensure that USVs are in camera view. The desirable FOV is more overhead.. 'rectangular' since it is a clearer picture than skewed for both human viewers and potential image processing applications, either onboard or post-processing. 

 
*Level 3: Anticipate direction:*

Relies on: USV positions, USV target positions.

Affects: Waypoint actuator, camera angle?

UAV uses the 'overall' directions of USVs to make a smoother path that keeps USVs in view more. 
Have not worked out the details, but instead of going into centroid, can set a waypoint that is a ahead or behind, but is along a the vector. 
Could use camera geometry to be such that more of the empty space in front of USVs, rather than behind. 


*Level 4: Smooth via models:*

Relies on: ??

Affects: ??

Idea is to use something like Kahlman filter to achieve smoother movement. Don't know enough about this to really comment. 








### Definitions

TARGETS = the set of all target surface vehicles.

TARGET = a single target surface vehicle such that TARGET is in TARGETS.

(TARGET.POX_X, TARGET.POS_Y) = The coordinates for current location of TARGET, as broadcast by TARGET.

(TARGET.DEST_X, TARGET.DEST_Y) = The coordinates for destination of TARGET, as broadcast by TARGET.

UAV = the single UAV responsible for maintaining view of all TARGETS.

(UAV.POX_X, UAV.POS_Y, UAV.POS_Z) = The coordinates for current location of UAV.

UAV.WAYPOINT = (UAV.DEST_X, UAV.DEST.Y) = The coordinates for destination of UAV.

UAV.DIR = The direction that UAV is facing within [0,360) degrees.

UAV.SPEED = Current speed of UAV.

UAV.MAX_SPEED = Maximum speed of UAV.

(UAV.IMG_X, UAV.IMG_Y) = Origin point of rectangular camera image captured by UAV when sufficiently overhead.

(UAV.IMG_X~, UAV.IMG_Y~) = Maximum corner point of rectangular camera image captured by UAV when sufficiently overhead.

TARGET_DIST = Ideal distance to maintain from TARGETS (central point) in order keep in view.

CURRENT_DIST = The current distance that UAV is from TARGETS (central point).

### Idea Overview

The goal of this idea was to have a very simple system based largely around reactive behaviors. 
The desired result is that UAV follows behind the TARGETS such that the their coordinates are all within the image:

		UAV.IMG.X < iTARGET.POS.X < UAV.IMG.X~ 
		UAV.IMG.Y < iTARGET.POS.Y < UAV.IMG.Y~ 

UAV receives the coordinates of all TARGETS and computes a central point to set as UAV.WAYPOINT.
UAV.SPEED is dynamically modified such that it is expected to end up behind and following the TARGETS.
The UAV.SPEED is defined by this piece-wise function:

		UAV.SPEED = [ (TARGET_DIST - CURRENT_DIST) / (TARGET_DIST) ] (UAV.SPEED)    if CURRENT_DIST < TARGET_DIST
		UAV.SPEED = UAV.SPEED                                                       if CURRENT_DIST == TARGET_DIST
		UAV.SPEED = [ (TARGET_DIST + CURRENT_DIST) / (TARGET_DIST) ] (UAV.SPEED)    if CURRENT_DIST > TARGET_DIST

In other words, if the UAV is too close to the TARGETS, slow down.

If the UAV is too far from the TARGETS, speed up. Not shown in equation, but of course there would be a speed limit, UAV.MAX_SPEED.

If the UAV is at the ideal distance, maintain speed. 

Since UAV.WAYPOINT is periodically re-calculated, UAV.DIR should be approximately correct at any given time. 

Depending on the spread of the TARGET's positions, raise or lower UAV.POS_Z to expand or contract camera's field of view. 

### Issues

Even if you threshold TARGET_DIST, we expect that there will be jerky movement along edges of piecewise function. 
An idea was proposed to use a Kalman Filter to reduce this.
