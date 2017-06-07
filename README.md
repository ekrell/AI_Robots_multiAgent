**Project has moved**

https://github.com/ekrell/menelaus

## AI Robots: P6 Multi-Agent Coordination

The purpose of this project is to coordinate a hetergeneous team of unmanned vehicles for
search and rescue applicatons in a water environment. The specfic (initial) goal is for a
single UAV to support multiple USVs by following the group and keeping each USV in camera view.

The target USV platform is the EMILY (emilyrobot.com). To differentiate, whenever a UGV is used
in the simulator in place of the USV, the robot is called MARISA.

### Developers

Evan Krell (evan.krell@tamucc.edu)

Arun Prassanth Ramaswamy Balasubramanian

Clayton Dittman	(clayton.dittman@tamu.edu)


### Directory Organization and Major Files
		documentation:
			InterfaceDiagram.png: System interface design diagram
			classDiagram.png: System class diagrams
		simulation: A version of the project based around the Morse simulator
			prototyping: where algorithms are tested on simulation data
				predictPath.py: Quadcopter prediction and positioning modules tested
				evaluate.py: The logs from predictPath are compared to the observed paths 
				statisticalAnalysis.R: Analysis of predictPath.py results
			lib: libraries, modules
			scenes: scripts that setup Morse environments with robots, terrain, sensors, etc
			robots: scripts that implement behaviors and such for Morse robots
			scripts: scenarios that use the robots to do tasks in a Morse scene
			inData: Waypoints and Starting positions for Morse robots
			outData: Simulations run output
		implementation: A version of the project that runs on actual hardware (In Progress)

### Qick Start - Test the quadcopter positioning prototype

0. Be at the top level of this repository

1. Run the predictPath script which does both path prediction and positioning

		python3 simulation/prototyping/predictPath.py -n susan,django,anton \
			-w simulation/inData/round12/ -p simulation/outData/round12/ > simulation/outData/test.csv

2. Use the evaluation script to see what percent targets were kept in view

		python3 simulation/prototyping/evaluate.py -n susan,django,anton \
			-w simulation/inData/round12/ -p simulation/outData/round12/ -f simulation/outData/test.csv

### Quick Start - Deploy a robot in Morse

0. Software Requirements (See ###MacOS Setup for setup on Apple Computer)

		apt-get install morse-simulator
		pip3 install pymorse


1. Configure python path to find our libraries (!! Look for smoother solution)

		export PYTHONPATH="${PYTHONPATH}:/<whatever_your_path>/AI_Robots_multiAgent/simulation/lib"


2. Set up scene

		morse run simulation/scenes/field_exercise_1.py

3. Configure the robot named 'Susan' to be a MARISA UGV robot (will run a test case)

		python3 simulation/robots/marisa.py -n susan -w simulation/inData/susan.waypoints




### MacOS Setup- Simulation

0. Update everything including xCode from the App Store and install Command Line Utilities
		
		Https://itunes.apple.com/app/xcode/id497799835?mt=12

1. Install brew package manager
	Execute In terminal	
	
		'/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'

3. Install Blender
	1. Execute in terminal
		
		brew install Caskroom/cask/blender
		
	2.  Create reference to blender by adding i. to your profile such as in ii.
		
		MORSE_BLENDER=/Applications/Blender.app/Contents/MacOS/blender
			
		sudo nano /etc/bashrc

	3.  Append the following string to bashrc file 
	
		export MORSE_BLENDER=/Applications/Blender.app/Contents/MacOS/blender

4. Install Python 3  (At the time of this writeup the proper version of python to use is python 3.5.2 and brew does not have any old versions on tap so you download and install manually which is trivial)
	1. Download and install Python3 @ https://www.python.org/downloads/release/python-352/
	2. You may want to check and verify your python version by executing the following in terminal
		
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
		
8. Return to Quick Start Simulation at the top.  

9. Sources
	- https://www.openrobots.org/morse/doc/stable/user/installation/package_manager/homebrew_osx.html
	- https://github.com/morse-simulator/homebrew-morse
	- https://github.com/caskroom/homebrew-cask/blob/master/Casks/blender.rb


10. additionall libraries you may need to install using pip
	- matplotlib
	- scipy
	- shapely
	- numpy
