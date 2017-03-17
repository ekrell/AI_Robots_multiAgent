# UAV : QCOORD
# This script sets up the specification of a UAV in the morse simulator
# Simulates a UAV quadcopter that follows and records UGV/USV

# The UAV has the following characteristics:
#   Base: QUAD2012
#   Sensors:
#       Pose - knows own location & rotation (simulates GPS and IMU)
#       VideoCamera - RGBA image video camera
#   Actuators:
#       Waypoint - can got to specified location (simulate autopilot)
#       MotionVW - can move given velocity vector (simulate motion control)

# Import libraries
import pymorse
import argparse
import time
import numpy as nm

# Import interfaces
from roboutils import get_status

# Import behaviors
from roboutils import ping
from roboutils import goto_target
from roboutils import return_home
from roboutils import halt


def systems_check(robot):

    # Very that robot is available
    if (ping(robot) == None):
        print ("[-] Robot {0} offline".format(robot['name']))
        return None
    print ("[+] Robot {0} online".format(robot['name']))

    # Verify 'pose' sensor
    try:
       getattr(simu, robot['name']).pose
       print("[+] Robot {0} sensor: pose online".format(robot['name']))
    except:
        print("[+] Robot {0} sensor: pose offline".format(robot['name']))
        return None

    # Verify 'waypoint' sensor
    try:
       getattr(simu, robot['name']).waypoint
       print("[+] Robot {0} actuator: waypoint online".format(robot['name']))
    except:
        print("[+] Robot {0} actuator: waypoint offline".format(robot['name']))
        return None

    # Verify 'motionWM' sensor
    try:
       getattr(simu, robot['name']).motion
       print("[+] Robot {0} actuator: motion online".format(robot['name']))
    except:
        print("[+] Robot {0} actuator: motion offline".format(robot['name']))
        return None

    print ("[+] Robot {0}: All systems online".format(robot['name']))
    return 0


def clear_targets(robot):
    robot['targets'] = set()

def add_targets(robot, inserts):
    robot['targets']  = robot['targets'] | inserts

def delete_targets(robot, deletions):
    robot['targets'].discard(deletions) 

def init_targets(robot, init):
    robot['targets'] = set(init)

def get_num_targets(robot):
    return len(robot['targets'])

def subscribe_to_targets(robot):
    return 0

def get_target_position(robot, xy):
    # STUB!
    # Instead of real robot data, pull from xy
    return xy


def follow_targets(robot, delta, initSpeed):
    speed = initSpeed

    # Make stack of fake target position
    positions = list(reversed([{'x':5, 'y':-3}, {'x':17, 'y':-3}, {'x':17, 'y':-3}, {'x':19, 'y':-3}, {'x':21, 'y':-3}, {'x':22, 'y':-3}, {'x':35, 'y':-3}, {'x':37, 'y':-3}]))
    
    while (len(positions) > 0):
        #dest = get_target_position(robot, positions.pop())
        pos = simu.susan.pose.get()
        dest = {'x':pos['x'], 'y':pos['y']}
        goto_target(robot, dest, speed);
        #while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
        #    print(str(get_status(robot)))
        time.sleep(0.5)


        # Calculate distance to destination
        status = get_status(robot); # Get own position
        distance = nm.sqrt(((dest['x'] - status['pos_x']) ** 2 ) + ((dest['y'] - status['pos_y']) ** 2 ))
	
        # Modify speed based on target distance from destination
        if (distance > delta + 1 and speed <= robot['MAX_SPEED']):
            speed = speed * (delta + distance) / delta
        elif (distance < delta - 1):
            speed = speed * (delta - distance) / delta

    return 0



# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help = "name of robot in MORSE environment")
parser.add_argument("-m", "--maxTargets", help = "max number of targets to monitor", default = 1)
parser.add_argument("-s", "--maxSpeed", help = "max speed of QCOORD", default = 5)
args = parser.parse_args()

# A robot is a dictionary of info
# Will fail if args not set => implicit argument verification
robot = {}

with pymorse.Morse() as simu:

    try:
        # Init robot
        robot = { 'name':args.name,
         'simu':simu,
         # Set of targets to monitor 
         'targets':set(), 
         'MAX_TARGETS':args.maxTargets,
         # Traits
         'MAX_SPEED':args.maxSpeed }

        systems_check(robot)
        targets = set(["susan"])
        init_targets(robot, targets)

        #goto_target(robot, {'x':7, 'y':-3}, 1.0)
        #time.sleep(0.5);
        #while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
        #    print(str(get_status(robot)))
        #    time.sleep(0.5)
        #halt(robot)

        follow_targets(robot, 2, 1)
        halt(robot)

    except pymorse.MorseServerError as mse:
        print('Oops! An error occured!')
        print(mse)

