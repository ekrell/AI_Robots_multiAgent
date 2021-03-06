# UGV : MARISA
# This script sets up the specification of a UGV in the morse simulator
# Simulates a simple ground robot with PIXHAWK 

# The UGV has the following characteristics:
#   Base: ATRV
#   Sensors: 
#       Pose - knows own location & rotation (simulate GPS and IMU)
#   Actuators:
#       Waypoint - can go to specified location (simulate autopilot)
#       MotionVW - can move given velocity vector (simulate motion control)

# Import libraries
import pymorse
import argparse
import datetime
import time

# Import interfaces
from roboutils import get_status

# Import behaviors
from roboutils import ping
from roboutils import goto_target
from roboutils import circle_target
from roboutils import return_home
from roboutils import circular_sweep
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



# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help = "variable name of robot in MORSE simulator")
parser.add_argument("-w", "--waypoints", help = "file containing waypoints")
args = parser.parse_args()

# Read waypoints
if (args.waypoints is not None):
    with open (args.waypoints) as f:
        waypoints = f.readlines ()
    waypoints = [x.strip () for x in waypoints]
    waypoints = [(float (x.split(',')[0]), float (x.split(',')[1])) for x in waypoints]
    print (waypoints)

# A robot is a dictionary of info
# Will fail if args not set => implicit argument verification
robot = {}

with pymorse.Morse() as simu:

    try:
        # Init robot using args and a Null destination
        robot = { 'name':args.name, 'destination':{'x':None, 'y':None}, 'simu':simu }

        systems_check(robot)
        print (str(get_status(robot)))
        
        if (args.waypoints):
            for w in waypoints:
                goto_target (robot, {'x':w[0], 'y':w[1]}, 2.0)
                while (getattr (simu, robot['name']).waypoint.get_status() == "Transit"):
                    print (str(get_status(robot)))
                    time.sleep(0.5)
                print ("Arrived!")
                #halt(robot)

        ##goto_target(robot, {'x':50, 'y':-50}, 2.0)
        ##while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
        ##    print ('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        ##    print (str(get_status(robot)))
        ##    time.sleep(0.5)
        ##halt(robot)
        ##circle_target(robot, {'x':-7, 'y':-7}, 3, 2, 2)

    except pymorse.MorseServerError as mse:
        print('Oops! An error occured!')
        print(mse)
    
