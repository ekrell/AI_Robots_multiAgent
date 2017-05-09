
import pymorse
import robomath as rm
import datetime
import time

def ping(robot):
    try:
        ping = getattr(robot['simu'], robot['name'])
    except:
        ping = None
    return ping


def get_position(robot):
    pose = getattr(robot['simu'], robot['name']).pose.get()
    pos = {'x':pose['x'], 'y':pose['y'], 'z':pose['z']}
    return pos

def get_orientation(robot):
    pose = getattr(robot['simu'], robot['name']).pose.get()
    orientation = {'pitch':pose['pitch'], 'roll':pose['pitch'], 'yaw':pose['yaw']}
    return orientation

def get_status(robot):
    destination = robot['destination']
    location =  get_position(robot)
    status = { 'time':'{:%H:%M:%S}'.format(datetime.datetime.now()),'pos_x':location['x'], 'pos_y':location['y'], 'dest_x':destination['x'], 'dest_y':destination['y'] }
    return status

def cancel_target(robot):
    getattr(robot['simu'], robot['name']).waypoint.stop()

def halt(robot):
    robot['destination'] = {'x':None, 'y':None}
    # case 1: robot moving because of waypoint
    cancel_target(robot)
    # case 2: robot moving because of motionVW
    getattr(robot['simu'], robot['name']).motion.set_speed(0.0, 0.0)

def motion_circle(robot, radius, speed_angular):
    speed_linear = (radius) * speed_angular
    getattr(robot['simu'], robot['name']).motion.set_speed(speed_linear, speed_angular)

def goto_target(robot, target, speed):
    robot['destination'] = target
    getattr(robot['simu'], robot['name']).waypoint.publish(
            {'x':target['x'], 'y':target['y'], 'z':10.0,
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
    while (getattr(robot['simu'], robot['name']).waypoint.get_status() == "Transit"):
        time.sleep(0.5)
    halt(robot)
    motion_circle(robot, radius, speed_angular)

def return_home(robot):
    return 0

def circular_sweep(robot):
    return 0


