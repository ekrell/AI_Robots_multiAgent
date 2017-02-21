## AI Robots: multi-agent team

The purpose of this project is to coordinate a hetergeneous team of unmanned vehicles for
search and rescue applicatons in a water environment. The specfic (initial) goal is for a 
single UAV to support multiple USVs by following the group and keeping each USV in camera view. 

The target USV platform is the EMILY (emilyrobot.com). To differentiate, whenever a UGV is used 
in the simulator in place of the USV, the robot is called MARISA. 

### Developers
Arun Prassanth Ramaswamy Balasubramanian

Clayton Dittman

Evan Krell - evan.krell@tamucc.edu

### Directory Organization
		documentation: 
		simulation: A version of the project based around the Morse simulator
			lib: libraries, modules
			scenes: scripts that setup Morse environments with robots, terrain, sensors, etc
			robots: scripts that implement behaviors and such for Morse robots
			scripts: scenarios that use the robots to do tasks in a Morse scene
			test: unit testing
		implementation: A version of the project that runs on actual hardware


### Quick Start - Simulation
Note that this is a very early stage. Some amount of organization/modularity is present, but
in the case of setting up the MARISA robot. 

0. Software Requirements

		apt-get install morse-simulator
		pip3 install pymorse


1. Configure python path to find our libraries (!! Look for smoother solution)

		export PYTHONPATH="${PYTHONPATH}:/<whatever_your_path>/AI_Robotics_multiAgent/simulation/lib"


2. Set up scene

		morse run simulation/scenes/field_exercise_1.py

3. Configure the robot named 'Susan' to be a MARISA UGV robot

		python3 simulation/robots/marisa.py -n susan
			



