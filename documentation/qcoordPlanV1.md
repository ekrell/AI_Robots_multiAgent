## QCOORD: Track multiple surface vehicles

This document describes basic ideas for implementing an algorithm that allows a single UAV to constantly reposition itself to keep multiple surface vehicles in view.


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
