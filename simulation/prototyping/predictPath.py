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

# Time between updates (s)
deltaT_s = .5     # Supposed interval between each periodic observation
deltaTT_s = .5   # Interval between estimated positions

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
        skip = 10
        for i in range(skip):
            if (len (t['observed_path']) > 1):
            
                t['position'] = t['observed_path'].pop (0)
                if (t['position'] == 'A'):
                    if (t['observed_path']):
                        t['position'] = t['observed_path'].pop (0)
                        t['waypoints'].pop(0)
                    else:
                        t['position'] = t['position_prev']
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

def rotatePoint(centerPoint,point,angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    angle = angle
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point

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
        paths['time'] = t['position'][2]  # ! Is written over each time, but matters little since all ~same time

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

        # If speed is 0, no path.. 
        if (t['speed'] != 0):
            cnt = 0 
            while (w is not None): # and cnt < 5000): # While waypoints still exist, continue building path prediction
                cnt = cnt + 1
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
       

#### Main 

def main ():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--names", help = "comma-separated list of target names")
    parser.add_argument("-w", "--waypoint_dir", help = "directory containing waypoint data")
    parser.add_argument("-p", "--path_dir", help = "directory containing path data")
    args = parser.parse_args()
    
    if (args.names is None):
        print ("Must supply targets with -n")
        exit (0)
    
    
    target_names = args.names.split (",")
    print (target_names)
    
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
        with open (fh) as f:
            path = f.readlines ()
            for line in path:
                line = line.rstrip()
                if (line == "Arrived!"):
                    t['observed_path'].append ('A')
                else:
                    time = re.findall('time[^,}]*', line)[0]
                    time = re.findall('[0-9]*:[0-9]*:[0-9]*', time)[0]
                    x = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_x[^,}]*', line)[0])[0]
                    y = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_y[^,}]*', line)[0])[0]
                    t['observed_path'].append ( (float (x), float (y), time) )
    
 
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
    pl.axis ((x1 - 10, x2 + 10, y1 - 10 , y2 + 10))
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
    
    updatePositions (targets)

    # Main loop: Path prediction
    numRuns = 0
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
        pl.plot(*zip(*paths['susan']), 'go')
        pl.plot(*zip(*paths['anton']), 'bo')
        pl.plot(*zip(*paths['django']), 'ro')
        pl.plot(*zip(*centroid_path['path']), 'mo')
        ####### End Plot
        numRuns = numRuns + 1
        #print (paths)
        print (centroid_path)
    pl.savefig ('predictPath__predicted.pdf')
    


if __name__ == "__main__":
    main()
