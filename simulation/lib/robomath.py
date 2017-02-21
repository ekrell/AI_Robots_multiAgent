# Various math calculations useful for robots

# Import libraries
from numpy.linalg import norm
from numpy import dot
import numpy as nm
import math


def get_angle_2D(a, b):
# Calculate the angle between two vectors in (R^2)
# a - a 2D numeric array
# b - a 2D numeric array
  x = dot(a, b) / norm(a) / norm(b)
  x = 1.0 if x > 1.0 else x
  x = -1.0 if x < -1.0 else x
  x = math.acos(x)
  return x

def get_coords_in_radius(t, s, r):
# Calculate the x,y coordinates needed
# to set a waypoint such that a point
# will go to the nearest point to a target,
# but at a radius r from it.
# t - target, a 2D numeric array
# s - current location, a 2D numeric array
# r - radius, a number
    theta = get_angle_2D (s, t)
    w = nm.subtract (s,t)
    w_norm = norm (w)
    coords = nm.add (t, nm.multiply (r, (w / norm (w))))
    return coords

