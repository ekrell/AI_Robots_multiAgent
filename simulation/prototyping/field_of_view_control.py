"""
File:   field_of_view_control.py

This file is calculates the FOV, stand-off distance etc. from the location of
the targets and makes decisions for tilt, zoom (camera) and yaw and other
manuvers of the UAV.

The basic idea is continuously loop thru the functions of
(verifying the existence of the target within FOV, maintain targets witin FOV
by by invoking correponding functions: yaw towards target, tilt camera,
calculate stand-off distance, move towards target etc.) All the required params
are then populated in a struct and send to the UAV.

As of now ,this module does NOT consider the predictions from the predictPath
module and this would be done later. Also not all the functionality need not be
in this file, they could be segregated based on the nature  ex. calculating FOV
and verification as one module while the maneuvers as a different module.

"""


"""
UAV UPDATE MSG STRUCTURE
=======================================================================
struct uav_control_params
{
    int x_delta ;   //move fwd or backwards
    int y_delta ;   //move sideways
    int z_delta ;   //move up/down

    int yaw_delta;  //(rotation about z axis)

    int standoff;   //standoff distance
    int speed ;     // more the distance, faster should go

    int tilt;       //gimbal tilt up down (angle range)
    int zoom;       //zoom in steps (0 being no zoom)
};
========================================================================
"""

from planar import BoundingBox

"""
Function: BoundingBox
INPUTS:
    co-ordinates of the EMILY's
OUTPUT:
    two coordinate points (max and minimum coordinate for the bounding rectangle)

DETAILS:
    The returned boundingBox box is with the minimum area i.e it exactly
    encloses all the points (max and min values lie  on the BoundingBox).

    Our requirement could be interpreted as: keeping this bounding box within
    the FOV. We also need to consider that the points would be in motion. It
    would be efficient to have some slack in the heading direction (derived
    from the predicitPath module) and keeping the FOV closer to the lower edge
    of the BoundingBox. This way we could increase the duration of the targets
    lying within the FOV.

    Also before calculating the FOV and maneuvering the UAV, stand-off distance
    must be calculated (Move closer if distance is more or vice versa).
"""
bbox = BoundingBox([(0,0), (1,2), (-5,6), (-3,2), (0.5,-1)])

#for math verification
print(bbox)


def check_targets(input_coordinates):
   """
PRIMARY FUNCTION WHICH INVOKES VARIOUS OTHER MINOR FUNCTIONS

   :param       input_coordinates
   :return:     none

   :details:
   Verify if the targets exist within the current FOV. Complex : Need to project
   the UAV's current FOV in terms of GPS co-ordinates (with only current GPS
   co-ordinate of UAV, altitude, camera resolution and aspect-ratio).

   PSEUDO CODE:
    If not within FOV
        target heading in same direction (same line of sight)
            zoom: if zoom would help
            tilt: if tilting camera would help
            move closer if neither helps (reduce standoff distance)
        target not within line of sight
            yaw: check if changing yaw would help (targets are moving sideways)
    If within FOV
        check in which quadrant the targets are predominantly (divide into 4 quadrants)
            tilt/yaw/move accordingly

   """
    return []


def calculate_standoff_distance( altitude, proximity_factor):
    """
 INPUTS:
   altitude:
        For time being  altitude is assumed as 1 (1=100ft, 1.1 = 110 ft etc.)
        altitude range could be something like 0.3(30 ft) to 3.9 (390 ft) - this
        max and min altitude can be set thru the initial configuration file
    proximity_factor:
        Can range between 0 - 1
        ex: 0.1 would take the UAV closer while 0.9 would increase the standoff
        distance
        ------------------------------
        NOTE: The idea of introducing proximity_factor and calculating standoff
        distance wrt to altittude are only for a better flexibility. It would
        be much simpler to fix on a distance within a permissible range for
        a particular altitude (ex. 5m minimum distance, move closer if distance
        is more than 20m).
        ------------------------------
 RETURN VALUE:
    standoff:
        Integer value which could be directly translated to distance in meters.
        0 - If tilting or zoom would work no need to move closer
    """

    #TODO
        #check if tilting/zooming the camera would work

    return []

#assume
input_coordinates = []
altitude = 1
proximity_factor = 0.5
yaw_delta = 0


check_targets( input_coordinates)

#yaw control



#get standoff distance
standoff = calculate_standoff_distance ( altitude, proximity_factor)




move_UAV(standoff_new)

print(bbox.center)
