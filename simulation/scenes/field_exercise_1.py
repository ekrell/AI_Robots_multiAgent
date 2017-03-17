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
pose_susan = Pose ()
pose_susan.name = "pose"
pose_susan.translate (z = 0.83)
pose_susan.add_interface ('socket')
susan.append (pose_susan)
waypoint_susan = Waypoint ()
waypoint_susan.name = "waypoint"
susan.append (waypoint_susan)
waypoint_susan.add_interface ('socket')
motion_susan = MotionVW ()
motion_susan.name = "motion"
susan.append (motion_susan)
motion_susan.add_interface ('socket')

# Initialize GODOT
godot = Quadrotor ()
godot.translate (x = -3.0, y = -3.0, z = 10.0)
godot.properties (Object = True, Graspable = False, Label = "GODOT")
pose_godot = Pose ()
pose_godot.name = "pose"
godot.append(pose_godot)
pose_godot.add_interface ('socket')
waypoint_godot = Waypoint ()
waypoint_godot.name = "waypoint"
waypoint_godot.RemainAtDestination = True
godot.append (waypoint_godot)
waypoint_godot.add_interface ('socket')
motion_godot = MotionVW ()
motion_godot.name = "motion"
godot.append (motion_godot)
motion_godot.add_interface ('socket')

# Setup environment
env = Environment('outdoors')
env.set_camera_location([5.0, -1.0, 30.0])
env.set_camera_rotation([0, 0, 0])
