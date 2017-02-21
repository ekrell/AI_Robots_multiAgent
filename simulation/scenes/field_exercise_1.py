# A Morse scene: 
# Environment: outdoors

# Robots:
#    DJANGO - UGV
#       platform: ATRV
#       sensors: { }
#       actuators: { Keyboard }
#    SUSAN - UGV
#       platform: ATRV
#       sensors: { Pose }
#       actuators: { Waypoint, MotionVW }
#    GODOT - UAV
#       platform: quadrotor
#       sensors: WIP
#       actuators: WIP

from morse.builder import *

# Initialize DJANGO
django = ATRV ()
django.translate (x = 1.0, z = 0.2)
django.properties (Object = True, Graspable = False, Label = "DJANGO")
keyboard = Keyboard ()
keyboard.properties (Speed = 3.0)
django.append (keyboard)

# Initialize SUSAN
susan = ATRV ()
susan.translate (x = 1.5, z = 0.2)
susan.properties (Object = True, Graspable = False, Label = "SUSAN")
pose = Pose ()
pose.translate (z = 0.83)
pose.add_interface ('socket')
susan.append (pose)
waypoint = Waypoint ()
susan.append (waypoint)
waypoint.add_interface ('socket')
motion = MotionVW ()
susan.append (motion)
motion.add_interface ('socket')

# Setup environment
env = Environment('outdoors')
env.set_camera_location([5.0, -1.0, 30.0])
env.set_camera_rotation([0, 0, 0])
