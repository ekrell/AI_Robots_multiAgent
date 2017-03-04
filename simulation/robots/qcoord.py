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

def subscribe_to_targets(robot):
    return 0;

def follow_targets(robot):
    return 0



# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help = "variable name of robot in MORSE simulator")
args = parser.parse_args()

# A robot is a dictionary of info
# Will fail if args not set => implicit argument verification

with pymorse.Morse() as simu:

    try:
        robot = { 'name':args.name,
         'simu':simu,
         # Set of targets to monitor 
         'targets':set(), 
         'MAX_TARGETS':2 }

        systems_check(robot)
        targets = set(["susan"])
        init_targets(robot, targets)

        goto_target(robot, {'x':7, 'y':-3}, 1.0)
        while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
            time.sleep(0.5)
        halt(robot)

    except pymorse.MorseServerError as mse:
        print('Oops! An error occured!')
        print(mse)

