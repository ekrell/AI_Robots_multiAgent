#!/usr/bin/python3
import math
import numpy as nm
import pylab as pl

#### Hard-coded testing data; Will actually come from inputs

# Target robots
E1 = { 'name':"E1", 'position_prev': (None, None), 'position': (3, 7), 'source': (3,7), 'speed': None,
    'waypoints': [(10, 15), (30, 20), (50, 25)] }
E2 = { 'name':"E2", 'position_prev': (None, None), 'position': (4, -3), 'source': (4, -3), 'speed': None,
    'waypoints': [(12, 6), (25, 15), (50, 20)] }
E3 = { 'name':"E3", 'position_prev': (None, None), 'position': (5, -3), 'source': (5, -3), 'speed': None,
    'waypoints': [(13, 10), (27, 13), (55, 22)] }
targets = [E1, E2, E3]

# Time between updates (s)
deltaT_s = .5
deltaTT_s = .25

# Future positions (next states)
E1_future = [ (5, 10), (7, 13), (11, 16), (15, 17), (18, 17.5), (21, 18), (24, 18.5), 
    (27, 19), (30, 20), (33, 21), (36, 22), (38, 22), (44, 23), (48, 22) ]
E1_future.reverse()
E2_future = [ (7, 1), (10, 4), (13, 6), (17, 8), (20, 10), (24, 12), (26, 14), 
    (29, 15), (33, 16), (37, 17), (41, 18), (45, 19), (47, 20), (50, 20) ]
E2_future.reverse()
E3_future = [ (8, 1), (12, 4), (13, 6), (19, 8), (24, 10), (26, 12), (29, 14), 
    (33, 15), (38, 16), (40, 18), (44, 18.5), (46, 19), (50, 21), (55, 22) ]
E3_future.reverse()
futures = {'E1': E1_future, 'E2': E2_future, 'E3': E3_future}

# Functions

def get_angle_2D(a, b):
# Calculate the angle between two vectors in (R^2)
# a - a 2D numeric array
# b - a 2D numeric array
  x = nm.dot(a, b) / nm.linalg.norm(a) / nm.linalg.norm(b)
  x = 1.0 if x > 1.0 else x
  x = -1.0 if x < -1.0 else x
  x = math.acos(x)
  return x

def calc_centroid (targets):
    # Source: http://stackoverflow.com/questions/23020659/fastest-way-to-calculate-the-centroid-of-a-set-of-coordinate-tuples-in-python-wi
    points = [t['position'] for t in targets]
    x, y = zip (*points)
    l = len (x)
    return sum (x) / l, sum (y) / l

def get_Position (targets):
    hasPosition = True

    for t in targets:
        t['position_prev'] = t['position']
        if futures[t['name']]:
            t['position'] = futures[t['name']].pop()
        else:
            hasPosition = False
    return hasPosition
    	 
def calc_Speed (targets):
    for t in targets:
        t['speed'] = (((t['position'][0] - t['position_prev'][0]) ** 2 + (t['position'][1] - t['position_prev'][1]) ** 2 ) ** (.5)) / (deltaT_s)

def predict_Path (targets):
    for t in targets:
        # Init path list, where is every item is the next predicted point after a deltaTT interval
        waypoints = t['waypoints'].copy()
        # First predicted position is actual position
        p = t['position']
        # Get next waypoint
        w = waypoints.pop(0)
        # Set source point
        s = t['source']
        while (w is not None):
            # Calc angle between position and waypoint
            thetaPrime = nm.arccos ( (nm.dot (p, (1,0))) / ( ((p[0] ** 2 + p[1] ** 2 ) ** (0.5)) * ((1 ** 2 + 0 ** 2 ) ** (0.5)) ) )
            velocity = (nm.cos (thetaPrime) * t['speed'], nm.sin (thetaPrime) * t['speed'])
            pp = (velocity[0] * deltaTT_s, velocity[1] * deltaTT_s) # How far will go in delta_T
		
            # Rotate the little vector toward waypoint
            pp = list(pp)
            w = list(w)
            p = list(p)
            theta = get_angle_2D (pp, w)
            w = nm.subtract (pp, w)
            w_norm = nm.linalg.norm (w)
            
            # Add little vector to current position for next position
            coords = nm.add (p, pp)
            old_p = p 
            p = (coords[0], coords[1])

            # Need to see if waypoint reached ---> next waypoint
            dist_to_waypoint = ( (w[0] - s[0]) ** 2 + (w[1] - s[1]) ** 2 ) ** (.5)
            dist_to_newPoint = ( (p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2 ) ** (.5)
            if (dist_to_waypoint < dist_to_newPoint):
                if(waypoints):
                    s = w
                    w = waypoints.pop(0)
                    p = w
                else:
                    w = None

# Initialize Data

# Init previous positions to null
for t in targets:
    t['position_prev'] = (None, None)

# Init current positions with input

# Init speeds to None
for t in targets: 
    t['speed'] = None

# Init centroid
centroid = { 'position_prev': (None, None), 'position': calc_centroid (targets), 'speed': None, 'direction': (None, None) }

# Init 'predict' as true, the flag for loop continuation
predict = True


# Debug stuff
cnt = 0
types = ['ro', 'bo', 'go']
for t in targets:
    pl.plot(*zip(*futures[t['name']]), types[cnt])
    cnt = cnt + 1
#pl.show()
# Main loop: Path prediction
cnt = 1
while (predict == True):
    print (cnt)
    predict = get_Position (targets)
    if (predict == False): # No position --> no prediction
        break
    calc_Speed (targets)
    centroid['position'] = calc_centroid (targets)
    predict_Path (targets)
    cnt = cnt + 1
    
    exit (0)
