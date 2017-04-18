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

#### Hard-coded scenario data

# Structure: Target
# has the following fields: 
### name: Unique name of target
### position: Last observed target position
### position_prev: Single previous position memory; used with 'position' to estimate the speed 
### Source: At any given waypoint, the target is coming from the last waypoint or initial position
### Speed: Estimated speed of target
### Waypoints: Sequence of waypoints
E1 = { 'name':"E1", 'position_prev': (None, None), 'position': (3, 7), 'source': (3,7), 'speed': None,
    'waypoints': [(10, 15), (30, 20), (50, 25)] }
E2 = { 'name':"E2", 'position_prev': (None, None), 'position': (4, -3), 'source': (4, -3), 'speed': None,
    'waypoints': [(12, 6), (25, 15), (50, 20)] }
E3 = { 'name':"E3", 'position_prev': (None, None), 'position': (5, -3), 'source': (5, -3), 'speed': None,
    'waypoints': [(13, 10), (27, 13), (55, 22)] }
targets = [E1, E2, E3]

# Time between updates (s)
deltaT_s = .5     # Supposed interval between each periodic observation
deltaTT_s = .25   # Interval between estimated positions

# Future positions
# These are the 'observated' of the target's position at every deltaT_s
E1_future = [ (5, 10), (7, 13), (11, 16), (15, 17), (18, 17.5), (21, 18), (24, 18.5), 
    (27, 19), (30, 20), (33, 21), (36, 22), (38, 22), (44, 23), (48, 22) ]
E2_future = [ (7, 1), (10, 4), (13, 6), (17, 8), (20, 10), (24, 12), (26, 14), 
    (29, 15), (33, 16), (37, 17), (41, 18), (45, 19), (47, 20), (50, 20) ]
E3_future = [ (8, 1), (12, 4), (13, 6), (19, 8), (24, 10), (26, 12), (29, 14), 
    (33, 15), (38, 16), (40, 18), (44, 18.5), (46, 19), (50, 21), (55, 22) ]
futures = {'E1': E1_future, 'E2': E2_future, 'E3': E3_future}



#### Function Definitions

def updatePositions (targets):
    """
    Function : updatePositions
    Arguments:
        targets: List of 'Target' structs
    Purpose:
        Update the target's current position while also
        setting the target's previous position and updates
        the list of the target's future position by consuming the head. 
        If the target as reached the current waypoint, set a new waypoint
        and consume the previous. 
    """
    for t in targets:
        # The current position is now the previous position
        t['position_prev'] = t['position']
   
        w = t['waypoints'][0] # Get current waypoint
        if futures[t['name']]:
            # Set the new position
            t['position'] = futures[t['name']].pop (0)

            # Check if the current waypoint has been reached,
            #  if the distance to current waypoint is less than the distance to new point -> have reached waypoint.
            dist_old_way = ( (w[0] - t['position_prev'][0]) ** 2 + (w[1] - t['position_prev'][1]) ** 2 ) ** (.5)
            dist_old_new = ( (t['position'][0] - t['position_prev'][0]) ** 2 + (t['position'][1] - t['position_prev'][1]) ** 2 ) ** (.5)
            if (dist_old_new > dist_old_way):
                t['waypoints'].pop(0)
        else: # Have lost connection or other critical error
            return False
    return True

def get_angle_2D (a, b):
# Calculate the angle between two vectors in (R^2)
# a - a 2D numeric array
# b - a 2D numeric array
  x = nm.dot(a, b) / nm.linalg.norm(a) / nm.linalg.norm(b)
  x = 1.0 if x > 1.0 else x
  x = -1.0 if x < -1.0 else x
  x = math.acos(x)
  return x

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
    points = [t['position'] for t in targets]
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
        # Init path list, where is every item is the next predicted point after a deltaTT interval
        waypoints = t['waypoints'].copy()
        # First predicted position is actual position
        p = t['position']
        paths[t['name']] = [p]
        # Get and consume current waypoint
        w = waypoints.pop(0)
        # Set source point: where the path starts from
        s = t['source']
        
        while (w is not None): # While waypoints still exist, continue building path prediction
            # Create interval vector
            # Calc angle between position-vector and x-axis in order to break speed into (x, y) components
            thetaPrime = get_angle_2D (p, [1, 0])
            # Break the speed into (x, y) components
            velocity = (nm.cos (thetaPrime) * t['speed'], nm.sin (thetaPrime) * t['speed'])
            # calculate interval vector: (Xvelocity * interval Time,  Yvelocity * interval_Time)
            i = (velocity[0] * deltaTT_s, velocity[1] * deltaTT_s)
	
            # Rotate the vector toward waypoint
            i = list(i)
            w = list(w)
            p = list(p)
            theta = get_angle_2D (i, w)
            w = nm.subtract (i, w)
            w_norm = nm.linalg.norm (w)
            
            # Add little vector to current position for next position
            coords = nm.add (p, i)
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
                    p = w
                else:
                    w = None # No more waypoints => terminate prediction
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
    return centroid_path
       

#### Main 

def main ():
    # Initialize Data
    
    # Init previous positions to null
    for t in targets:
        t['position_prev'] = (None, None)

    # Init current positions
        #! Currently via hard-coded data
    
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
    pl.axis ((x1 - 2, x2 + 2, y1 - 2 , y2 + 2))
    pl.legend(loc='lower right', shadow=True)
    pl.savefig ('predictPath__waypoints.pdf')
    ####### End Plot
    
    ####### Plot: Observed target positions
    cnt = 0
    labels = ['Target 1: observed', 'Target 2: observed', 'Target 3: observed']
    for t in targets:
        pl.plot(*zip(*futures[t['name']]), linestyle = '-', color = cols[cnt], label = labels[cnt])
        cnt = cnt + 1
    pl.legend(loc='lower right', shadow=True)
    pl.savefig ('predictPath__observed.pdf')
    ####### End Plot
    
    # Main loop: Path prediction
    while (predict == True):
        predict = updatePositions (targets)
        if (predict == False): # No position --> no prediction
            break
        # Estimate target speeds
        calcSpeed (targets)
        # Calculate centroid using current observations
        centroid['position'] = calcCentroid (targets)
        # Predict the paths of the targets
        paths = predictPath (targets)
        # use targets' path predictions to predict centroid path
        centroid_path = calcCentroidPath (targets, paths)
        ####### Plot: Current path prediction
     
        ####### Plot: Predicted centroid paths
        pl.plot(*zip(*centroid_path), alpha = 0.7, color = 'grey')
        ####### End Plot
    pl.savefig ('predictPath__predicted.pdf')
    
