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
import robomath as rm

# === Functions: system ===

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



# === Functions: behaviors ===

def ping(robot):
    try:
        ping = getattr(simu, robot['name'])
    except:
        ping = None
    return ping


def get_position(robot):
    pose = getattr(simu, robot['name']).pose.get()
    pos = {'x':pose['x'], 'y':pose['y'], 'z':pose['z']}
    return pos

def get_orientation(robot):
    pose = getattr(simu, robot['name']).pose.get()
    orientation = {'pitch':pose['pitch'], 'roll':pose['pitch'], 'yaw':pose['yaw']}
    return orientation

def cancel_target(robot):
    getattr(simu, robot['name']).waypoint.stop()

def halt(robot):
    # case 1: robot moving because of waypoint
    cancel_target(robot)
    # case 2: robot moving because of motionVW
    getattr(simu, robot['name']).motion.set_speed(0.0, 0.0)

def motion_circle(robot, radius, speed_angular):
    speed_linear = (radius) * speed_angular
    getattr(simu, robot['name']).motion.set_speed(speed_linear, speed_angular)

def goto_target(robot, target, speed):
    getattr(simu, robot['name']).waypoint.publish(
            {'x':target['x'], 'y':target['y'], 'z':0.0,
                'tolerance':0.5, 'speed':speed})

def circle_target(robot, target, radius, speed_transit, speed_angular):
    halt(robot)
    # !! Does not yet take into account direction
    #   before starting circular motion. Might not
    #   actually circle target. 
    pos = get_position(robot)
    coords = rm.get_coords_in_radius(
            [target['x'], target['y']], 
            [pos['x'], pos['y']],
            radius)
    target_adj = {'x':coords[0], 'y':coords[1]}
    goto_target(robot, target_adj, speed_transit)
    # Begin cicular motion using LinearVelocity = (Radius)(AngularVelocity)
    while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
        simu.sleep(0.5)
    halt(robot)
    motion_circle(robot, radius, speed_angular)

def return_home(robot):
    return 0

def circular_sweep(robot):
    return 0


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help = "variable name of robot in MORSE simulator")
args = parser.parse_args()

# A robot is a dictionary of info
# Will fail if args not set => implicit argument verification
robot = { 'name':args.name }

with pymorse.Morse() as simu:

    try:
        systems_check(robot)
        print (get_position(robot))
        print (get_orientation(robot))
        goto_target(robot, {'x':-4, 'y':-3}, 1.0)
        while (getattr(simu, robot['name']).waypoint.get_status() == "Transit"):
            simu.sleep(0.5)
        halt(robot)
        circle_target(robot, {'x':-7, 'y':-7}, 3, 2, 2)

    except pymorse.MorseServerError as mse:
        print('Oops! An error occured!')
        print(mse)
    
