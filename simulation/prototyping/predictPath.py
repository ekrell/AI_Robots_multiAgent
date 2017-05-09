#!/usr/bin/python3

"""
File: predictPath.py

This script prototypes a multi-target path prediction algorithm.
The goal is to predict the path of a centroid as multiple targets follow waypoints.
Targets are allowed to differ in speed and waypoints, but are expected to be following
waypoints close together and at similar speeds because the targets are moving as a group 
toward the same or clustered goals. 

At the moment, the data is hard-coded into this script.
In the future, the data will be input from files to test the algorithm in diverse situations. 

The hard-coded scenario is this:
3 targets are initially within 11 units of each other. 
Each has own set of waypoints. The final waypoints are within 8 units of each other.
Each target has a number of periodic 'observations' that are not always aligned with the next waypoint
(to represent some variability such as environmental conditions or nonholonomic motion).
""" 
import math
import numpy as nm
import pylab as pl
import argparse
import re
from matplotlib.path import Path
import matplotlib.patches as patches
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Time between updates (s)
deltaT_s = 2    # Interval between target's position messages
deltaTT_s = 2   # Interval between estimated positions
maxWait = 5
useWaypoints = True


#### Function Definitions

def updatePositions (targets):
    """
    Function : updatePositions
    Arguments:
        targets: List of 'Target' objects
    Purpose:
        Update the target's current position while also
        setting the target's previous position and updates
        the list of the target's future position by consuming the head. 
        If the target as reached the current waypoint, set a new waypoint
        and consume the previous. 
    """
    done = 1
    for t in targets:
        # The current position is now the previous position
        t['position_prev'] = t['position']
        # Get current waypoint

        w = t['waypoints'][0]         
        if (len (t['observed_path']) > 0):
            t['position'] = t['observed_path'].pop (0)
            if (t['position'] == 'A'):
                if (len (t['observed_path']) > 0):
                    t['position'] = t['observed_path'].pop (0)
                    t['waypoints'].pop(0)
                else:
                    t['position'] = t['waypoints'][0]
                    t['position_prev'] = t['position']
            #t['position'] = t['waypoints'][0]
            #t['position_prev'] = t['position']
        else: # Have lost connection or other critical error
        #    t['position'] = t['waypoints'][0]
        #    t['position_prev'] = t['position']
             done = done + 1
    if (done == len (targets)):
        return False
    else:
        return True

def calcFieldOfView (camera):
    """
    Function: calcFieldOfView
    Arguments:
        camera: Camera object
    Purpose:
        Calculate the field of view (FoV) for a camera 
        given the x and y sensor dimensions and the focal length
    """
    xView = (2 * math.atan (camera['xSensor_mm'] / (2 * camera['focallen_mm'])))
    yView = (2 * math.atan (camera['ySensor_mm'] / (2 * camera['focallen_mm'])))
    return (xView, yView)

def calcGroundFootprintDimensions (camera, altitude_m):
    """
    Function: calcGroundFootprintDimension
    Arguments:
        camera: Camera object
        altitude_m: Altitude of camera in meters
    Purpose: 
        Calculate the ground footprint of an aerial camera, 
        such as one mounted on an aerial vehicle. 
        Finds distances relative to the camera position, but not the actual position
    """
    FoV = calcFieldOfView (camera)
    distFront = altitude_m * (math.tan(nm.radians (camera['xGimbal_deg']) + 0.5 * FoV[0])) 
    distBehind = altitude_m * (math.tan(nm.radians (camera['xGimbal_deg']) - 0.5 * FoV[0]))
    distLeft = altitude_m * (math.tan(nm.radians (camera['yGimbal_deg']) - 0.5 * FoV[1]))
    distRight = altitude_m * (math.tan(nm.radians (camera['yGimbal_deg']) + 0.5 * FoV[1]))
    return (distFront, distBehind, distLeft, distRight)

def calcGroundFootprint (camera, altitude_m, position):
    """
    Function: calcGroundFootprint
    Arguments: 
        camera: Camera object
        altitude_m: Altitude of camera in meters
        position: ground (x, y) coordinates of camera
    """
    (distFront, distBehind, distLeft, distRight) = calcGroundFootprintDimensions (camera, altitude_m)
    posLowerLeft = (position[0] + distLeft, position[1] + distBehind)
    posLowerRight = (position[0] + distRight, position[1] + distBehind)
    posUpperLeft = (position[0] + distLeft, position[1] + distFront)
    posUpperRight = (position[0] + distRight, position[1] + distFront)
    return (posLowerLeft, posUpperLeft, posUpperRight, posLowerRight)

def calcTimeToStayInPosition(centroidPath, footprint):
    polygon = Polygon (footprint)
    cPath = centroidPath.copy ()
    # First centroid assumed to be in footprint: increment by update interval
    time_s = deltaTT_s
    centroidContained = True
    while (centroidContained == True and len (cPath) > 0):
        nextCentroid = cPath.pop (0)
        point = Point (nextCentroid)
        # Check if the next centroid is in footprint
        if (polygon.contains (point)):
            # Since it is, increment by update interval
            time_s = time_s + deltaTT_s
        else:
            centroidContained = False 
    return time_s
    

def get_angle_2D (a, b):
    """
    Function: get_angle_2D
    Arguments:
        a: 2D numeric array 
        b: 2D numeric array
    Purpose:
    Calculate the angle between two vectors in (R^2)
    """
    x = nm.dot(a, b) / nm.linalg.norm(a) / nm.linalg.norm(b)
    x = 1.0 if x > 1.0 else x
    x = -1.0 if x < -1.0 else x
    x = math.acos(x)
    return x

def get_coords_in_radius(t, s, r):
    """
    Function: get_coords_in_radius
    Purpose:
        Calculate the x,y coordinates needed
        to set a waypoint such that a point          
        will go to the nearest point to a target
        but at a radius r from it.
    Arguments:
        t: target, a 2D numeric array
        s: current location, a 2D numeric array
        r: radius, a number
    """
    theta = get_angle_2D (s, t)
    w = nm.subtract (s,t)
    w_norm = nm.linalg.norm (w)
    coords = nm.add (t, nm.multiply (r, (w / nm.linalg.norm (w))))
    return coords

def rotatePoint(centerPoint,point,angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    # Source: https://gist.github.com/somada141/d81a05f172bb2df26a2c
    angle = angle
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point

def rotatePolygon(polygon,theta):
    """Rotates the given polygon which consists of corners represented as (x,y),
    around the ORIGIN, clock-wise, theta degrees"""
    # Source: https://gist.github.com/somada141/d81a05f172bb2df26a2c
    theta = math.radians(theta)
    rotatedPolygon = []
    for corner in polygon :
        rotatedPolygon.append(( corner[0]*math.cos(theta)-corner[1]*math.sin(theta) , corner[0]*math.sin(theta)+corner[1]*math.cos(theta)) )
    return rotatedPolygon


def calcCentroid (targets):
    """
    Function: calcCentroid
    Arguments:
        targets: List of 'Target' structs
    Purpose:
        Returns the center point of the current positions in all targets
    Source: 
        http://stackoverflow.com/questions/23020659/fastest-way-to-calculate-the-centroid-of-a-set-of-coordinate-tuples-in-python-wi
    """
    points = [(t['position'][0], t['position'][1]) for t in targets]
    x, y = zip (*points)
    l = len (x)
    return sum (x) / l, sum (y) / l

def calcSpeed (targets):
    """
    Function: calcSpeed
    Arguments:
        targets: List of 'Target' structs
    Purpose:
        Estimate a targets speed as (distance in time interval) / (time interval)
    """
    for t in targets:
        t['speed'] = (((t['position'][0] - t['position_prev'][0]) ** 2 + (t['position'][1] - t['position_prev'][1]) ** 2 ) ** (.5)) / (deltaT_s)

def predictPath (targets):
    """
    Function: predictPath
    Arguments:
        targets: List of 'Target' structs
    Purpose:
        Determines where it believes that the the targets will be after every time interval deltaTT_s
        by calculating a vector in each interval whose magnitude is equal to distance traveled at estimated speed
        and whose angle is aligned with the current waypoint. 
        Each interval's vector is added to current vector such that the cummulative vector sum is the estimated path.
        This is done for each Target in targets. 
    Returns: 
        A list whose entries are a list of the estimated interval positions (predicted path) for each target
    """

    # Init empty paths, where each path is accessable by target's name
    paths = dict.fromkeys( [t['name'] for t in targets] )    
    for t in targets:
        paths['time'] = t['position'][0]  # ! Is written over each time, but matters little since all ~same time

        # Init path list, where is every item is the next predicted point after a deltaTT interval
        waypoints = t['waypoints'].copy()
        # First predicted position is actual position
        p = (t['position'][0], t['position'][1])
        paths[t['name']] = [p]
        # Get and consume current waypoint
        w = waypoints.pop(0)
        # Set source point: where the path starts from
        t['source'] = t['position']
        s = t['source']

        # If speed is 0
        if (t['speed'] != 0):
            cnt_time = 0
            while (w is not None): # and cnt_time < 30): # While waypoints still exist, continue building path prediction
                cnt_time = cnt_time + 2
                i = (t['speed'] * deltaTT_s, 0)
                l = nm.subtract (p, w)
                tt = nm.arctan2(l[1], l[0])
                if (tt < 0):
                    tt = tt + 2 * math.pi
                i = rotatePoint ((0,0), i, tt) 

                # Add interval vector to current position for next position
                coords = nm.subtract (p, i)
                old_p = p 
                p = (coords[0], coords[1])
                # Add new postion to predicted path
                paths[t['name']].append (p)

                # Check if the current waypoint has been reached,
                #  if the distance to current waypoint is less than the distance to new point -> have reached waypoint.
                dist_to_waypoint = ( (w[0] - s[0]) ** 2 + (w[1] - s[1]) ** 2 ) ** (.5)
                dist_to_newPoint = ( (p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2 ) ** (.5)

                if (dist_to_waypoint < dist_to_newPoint):
                    if(waypoints):
                        s = w
                        w = waypoints.pop(0)
                        p = s
                    else:
                        w = None # No more waypoints => terminate prediction
        else:
            # Stationary targets
            paths[t['name']].append (p)
    return paths

def calcCentroidPath (targets, paths):
    """
    Function: calcCentroidPath
    Arguments:
        targets: List of 'Target' structs
        paths: predicted path for each target
    Purpose:
        Predicts the path of the target's centroid by taking the centroid of the predicted postitions at each interval.
    """
    centroid_path = []
    lenmax = max ([len (paths[t['name']]) for t in targets])
    for i in range (lenmax):
        # Each element in path array corrosponds to interval, but
        # Not all have to have the same length. Possible for targets to reach final waypoint at different
        # times. Thus, once a predicted path has ended, continue using the last element for that target
        state_t = [ paths[t['name']][i] if ( len(paths[t['name']]) > i ) else ( paths[t['name']][len(paths[t['name']]) - 1] ) for t in targets ]
        x, y = zip (*state_t)
        l = len (x)
        # Calculate centroid
        centroid = sum (x) / l, sum (y) / l
        # Add centroid to path
        centroid_path.append (centroid)
        # Assign centroid path time 
        time = paths['time']
    return {'path':centroid_path, 'time':time}
       

def main ():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--names", help = "comma-separated list of target names")
    parser.add_argument("-w", "--waypoint_dir", help = "directory containing waypoint data")
    parser.add_argument("-p", "--path_dir", help = "directory containing path data")
    parser.add_argument("-d", "--disable_waypoints", help = "disable using waypoints for following")
    args = parser.parse_args()
    
    if (args.names is None):
        print ("Must supply targets with -n")
        exit (0)
    target_names = args.names.split (",")

    if (args.disable_waypoints is not None):
        useWaypoints = False
    else:
        useWaypoints = True
    
    # Parse targets, waypoints, initial positions
    targets = [{'name':x, 'position_prev':(None, None), 'position':(None, None), 'source':(None, None), 'speed':None} for x in target_names]
    for t in targets:
        # Read waypoints
        fh = args.waypoint_dir + t['name'] + ".waypoints"
        with open (fh) as f:
            waypoints = f.readlines ()
        waypoints = [x.strip () for x in waypoints]
        t['waypoints'] = [(float (x.split(',')[0]), float (x.split(',')[1])) for x in waypoints]
    
        # Read start position
        fh = args.waypoint_dir + t['name'] + ".start"
        with open (fh) as f:
            start = f.readlines ()[0].strip ()
        t['position'] = (float (start.split(',')[0]), float (start.split(',')[1])) 
        t['source'] = t['position']
    
    
    # Parse target's observed path points
    for t in targets:
        fh = args.path_dir + t['name'] + ".path"
        t['observed_path'] = [t['source']]
        secs_prev = -1
        with open (fh) as f:
            path = f.readlines ()
            for line in path:
                line = line.rstrip()
                if (line[0] == '['):
                    # Ignore
                    True
                elif (line == "Arrived!"):
                    t['observed_path'].append ('A')
                else:
                    time = re.findall('time[^,}]*', line)[0]
                    time = re.findall('[0-9]*:[0-9]*:[0-9]*', time)[0]
                    # ! Only add uniq, even times
                    secs = time.split(":")[2]
                    if (int (secs) % 2 != 0):
                        # Ignore
                        True
                    elif (secs == secs_prev):
                        # Ignore
                        True
                    else:
                        x = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_x[^,}]*', line)[0])[0]
                        y = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_y[^,}]*', line)[0])[0]
                        t['observed_path'].append ( (float (x), float (y)) )
                    secs_prev = secs

    
    # Init Quadcopter
    quad = {'camera': {'xSensor_mm':6.16, 'ySensor_mm':4.62, 'focallen_mm':3.61, 'xGimbal_deg':0, 'yGimbal_deg':20}}
    quad['altitude'] = 75
    quad['position_prev'] = (-62, 60)
    quad['position'] = (-60, 60)
    quad['heading'] = 0
 
    # Init previous positions to null
    for t in targets:
        t['position_prev'] = (None, None)

    # Init speeds to None
    for t in targets: 
        t['speed'] = None
    
    # Init centroid
    centroid = { 'position_prev': (None, None), 'position': calcCentroid (targets), 'speed': None, 'direction': (None, None) }
    
    # Init 'predict' as true, the flag for loop continuation
    predict = True
    
    ####### Plot: Waypoints & initial positions
    pl.title ('Target Tracking')
    cnt = 0
    cols = ['r', 'b', 'g']
    labels = ['Target 1: waypoints', 'Target 2: waypoints', 'Target 3: waypoints']
    for t in targets:
        ways = []
        ways.append (t['position'])
        ways.extend (t['waypoints'])
        pl.plot(*zip (*ways), linestyle = '--', marker = 'o', color = cols[cnt], label = labels[cnt])
        cnt = cnt + 1
        pl.legend ()
    x1, x2, y1, y2 = pl.axis()
    pl.axis ((x1 - 50, x2 + 50, y1 - 50 , y2 + 50))
    pl.legend(loc='lower left', shadow=True)
    pl.savefig ('predictPath__waypoints.pdf')
    ####### End Plot
    
    ####### Plot: Observed target positions
    cnt = 0
    labels = ['Target 1: observed', 'Target 2: observed', 'Target 3: observed']
    for t in targets:
        path = [ (x[0], x[1]) if (x != "A") else (nm.nan, nm.nan) for x in t['observed_path'] ]
        pl.plot(*zip(*path), linestyle = '-', color = cols[cnt], label = labels[cnt])
        cnt = cnt + 1
    pl.legend(loc='lower left', shadow=True)
    pl.savefig ('predictPath__observed.pdf')
    ####### End Plot

    # Handles communication
    updatePositions (targets)

    # Main loop: Path prediction
    numRuns = 0
    timeRun = 0

    prev = None
 
    footDist = 0
 
    while (predict == True):
        
        # Should reposition?
        reposition = True        

        # Skip updates based off of loop, since
        numSkip = timeRun #/ deltaT_s)
        for i in range (numSkip):
            if (predict == True):
                 predict = updatePositions (targets)
        
        #-------------------------#
        # Phase 0: Estimate Speed #
        #-------------------------#
        
        # Estimate target speeds
        calcSpeed (targets)
        # Calculate centroid using current observations
        centroid['position'] = calcCentroid (targets)

        #--------------------------#
        # Phase 1: Path Prediction #
        #--------------------------#

        # Predict the paths of the targets
        paths = predictPath (targets)
        # use targets' path predictions to predict centroid path
        centroid_path = calcCentroidPath (targets, paths)
        
        ####### Plot: Predicted centroid paths
        #pl.plot(*zip(*paths['susan']), 'go')
        #pl.plot(*zip(*paths['anton']), 'bo')
        #pl.plot(*zip(*paths['django']), 'ro')
        #pl.plot(*zip(*centroid_path['path']), '.')
        ####### End Plot

        numRuns = numRuns + 1

        #------------------------#
        # Phase 2 : Positioning  #
        #------------------------#


        # Determine standoff distance
        points = [(t['position'][0], t['position'][1]) for t in targets]
        #c = (centroid['position'][0], centroid['position'][1])
        c = quad['position']
        lowDist = 100 # <---- embarrassing.. 
        maxDist = 0
        for t in targets: 
            p = t['position']
            distFromCentroid = ((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 ) ** (.5)
            if (distFromCentroid < lowDist):
                lowDist = distFromCentroid
                maxTarget = t
            if (distFromCentroid > maxDist):
                maxDist = distFromCentroid
                realMaxTarget = t
        standoffDist = 1
        
        if (maxDist < footDist - 1 ):
            reposition = False

        pl.plot ([maxTarget['position'][0]], [maxTarget['position'][1]], marker = 'x')
        
        # Set waypoint as first predicted centroid
        if (len (centroid_path['path']) > 1):
            nextCentroid = centroid_path['path'][1]
        else:
            nextCentroid = centroid_path['path'][0]
        #if (len (centroid_path['path']) > 5):
        #    futureCentroid = centroid_path['path'][4]
        #else:
        #     futureCentroid = nextCentroid

        # Get waypoint centroid
        nextWaypoints = [t['waypoints'][0] for t in targets]
        x, y = zip (*nextWaypoints)
        l = len (x)
        wayCenter = ( sum (x) / l, sum (y) / l )
        futureCentroid = wayCenter

## 
        if (useWaypoints == False):
            futureCentroid = nextCentroid

        # Go to waypoint
        if (maxTarget['position'][0] == quad['position_prev'][0] and maxTarget['position'][1] == quad['position_prev'][1]):
            reposition = False 
        if (reposition):
                quad['waypoint'] = get_coords_in_radius (maxTarget['position'], quad['position_prev'], standoffDist)
            #else: 
            #    quad['waypoint'] = get_coords_in_radius (maxTarget['position'], quad['position'], standoffDist)
        else:
            quad['waypoint'] = quad['position']
        quad['position_prev'] = quad['position']
        quad['position'] = quad['waypoint']

        # Set heading angle toward the waypoint
        if (reposition):
            p = quad['position_prev']
            w = quad['waypoint']
            n = futureCentroid
            i = nm.subtract (n, w)
            theta = nm.arctan2 (i[1], i[0])
            if (theta < 0):
                theta = theta + 2 * math.pi
            quad['heading_angle'] = theta

        # Get current ground footprint
        footprint =  calcGroundFootprint (quad['camera'], quad['altitude'], quad['position'])
        footprint = [rotatePoint (w, footprint[0], theta), 
                     rotatePoint (w, footprint[1], theta), 
                     rotatePoint (w, footprint[2], theta),
                     rotatePoint (w, footprint[3], theta)]
        footDist = calcGroundFootprintDimensions (quad['camera'], quad['altitude'])[0]
        # How long to stay in position
        timeToStayAtWaypoint = calcTimeToStayInPosition (centroid_path['path'], footprint)
        timeToStayAtWaypoint = min (timeToStayAtWaypoint, maxWait)
        timeToStatAtWaypoint = max (timeToStayAtWaypoint, 5)
        if (useWaypoints == False):
            timeToStayAtWaypoint = 10
        else:
            timeToStayAtWaypoint = 10
        
        # Logging:
        # Build CSV row of footprint information
        CSVrow = [str (f[0]) + "," + str (f[1]) + "," for f in footprint]
        CSVrow.append (str (timeToStayAtWaypoint))
        CSVrow = ''.join (CSVrow)
        print (CSVrow)
 
        ####### Plot: Footprint
        # Source = http://matplotlib.org/users/path_tutorial.html
        verts = footprint
        verts.append ( (0, 0) )
        codes = [Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
            ]
        path = Path (verts, codes)
        patch = patches.PathPatch (path, facecolor = 'orange', lw = 2)
        pl.gca().add_patch (patch)
        #######

        timeRun = timeToStayAtWaypoint
    pl.savefig ('predictPath__predicted.pdf')


if __name__ == "__main__":
    main()
