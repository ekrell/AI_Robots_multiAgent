## AI Robots: multi-agent team

The purpose of this project is to coordinate a hetergeneous team of unmanned vehicles for
search and rescue applicatons in a water environment. The specfic (initial) goal is for a
single UAV to support multiple USVs by following the group and keeping each USV in camera view.

The target USV platform is the EMILY (emilyrobot.com). To differentiate, whenever a UGV is used
in the simulator in place of the USV, the robot is called MARISA.

### Developers
---------NAME--------------------------		---------eMail------------	-----------Phone #-------------

Arun Prassanth Ramaswamy Balasubramanian

Clayton Dittman					clayton.dittman@tamu.edu 	

Evan Krell					evan.krell@tamucc.edu

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
in the case of setting up the MARISA robot... a quick test script is combined with the configuration script.

0. Software Requirements (See ###MacOS Setup for setup on Apple Computer)

		apt-get install morse-simulator
		pip3 install pymorse


1. Configure python path to find our libraries (!! Look for smoother solution)

		export PYTHONPATH="${PYTHONPATH}:/<whatever_your_path>/AI_Robots_multiAgent/simulation/lib"


2. Set up scene

		morse run simulation/scenes/field_exercise_1.py

3. Configure the robot named 'Susan' to be a MARISA UGV robot (will run a test case)

		python3 simulation/robots/marisa.py -n susan




### MacOS Setup- Simulation

0. Update everything including xCode from the App Store and install Command Line Utilities
		
		Https://itunes.apple.com/app/xcode/id497799835?mt=12

1. Install brew package manager
	Execute In terminal	
	
		'/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'

3. Install Blender	
	a. Execute in terminal
		
		brew install Caskroom/cask/blender
		
	b. Create reference to blender by adding i. to your profile such as in ii.
		
		MORSE_BLENDER=/Applications/Blender.app/Contents/MacOS/blender
			
		sudo nano /etc/bashrc

	c. Append the following string to bashrc file 
	
		export MORSE_BLENDER=/Applications/Blender.app/Contents/MacOS/blender

4. Install Python 3  (At the time of this writeup the proper version of python to use is python 3.5.2 and brew does not have any old versions on tap so you download and install manually which is trivial)
	a. Download and install Python3 @ https://www.python.org/downloads/release/python-352/
	b. You may want to check and verify your python version by executing the following in terminal
		
		echo 'import sys; print("VERSION %s" % sys.version.split()[0]); sys.exit(0)' > /tmp/version.py ${MORSE_BLENDER} -y -P /tmp/version.py 2>&1 | grep VERSION

5. Install pymorse
	Execute in terminal
		
		pip3 install pymorse

6. Install cmake dependency "pkg-config"
	 Execute in terminal		
		
		Brew install pkg-config"
	
7. Install Morse Simulator
	 Execute in terminal
	
		brew tap morse-simulator/morse; brew install morse-simulator;

8) Sources
	a. https://www.openrobots.org/morse/doc/stable/user/installation/package_manager/homebrew_osx.html
	b. https://github.com/morse-simulator/homebrew-morse
	c. https://github.com/caskroom/homebrew-cask/blob/master/Casks/blender.rb
