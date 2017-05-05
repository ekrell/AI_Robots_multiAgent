import math
import numpy as nm
import pylab as pl
import argparse
import re
from matplotlib.path import Path
import matplotlib.patches as patches
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def main ():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--names", help = "comma-separated list of target names")
    parser.add_argument("-w", "--waypoint_dir", help = "directory containing waypoint data")
    parser.add_argument("-p", "--path_dir", help = "directory containing path data")
    parser.add_argument("-f", "--coverage_file", help = "CSV file with ground footprint and time")
    args = parser.parse_args()

    if (args.names is None):
        print ("Must supply targets with -n")
        exit (0)
    target_names = args.names.split (",")

    # Parse targets, waypoints, initial positions
    targets = [{'name':x, 'position_prev':(None, None), 'position':(None, None), 'source':(None, None), 'speed':None} for x in target_names]
    for t in targets:
        # Read waypoints
        fh = args.waypoint_dir + t['name'] + ".waypoints"
        with open (fh) as f:
            waypoints = f.readlines ()
        waypoints = [x.strip () for x in waypoints]
        t['waypoints'] = [(float (x.split(',')[0]), float (x.split(',')[1])) for x in waypoints]

        # Read start position
        fh = args.waypoint_dir + t['name'] + ".start"
        with open (fh) as f:
            start = f.readlines ()[0].strip ()
        t['position'] = (float (start.split(',')[0]), float (start.split(',')[1]))
        t['source'] = t['position']


    # Parse target's observed path points
    for t in targets:
        fh = args.path_dir + t['name'] + "_2s.path"
        t['observed_path'] = [t['source']]
        with open (fh) as f:
            path = f.readlines ()
            for line in path:
                line = line.rstrip()
                if (line == "Arrived!"):
                    t['observed_path'].append ('A')
                else:
                    time = re.findall('time[^,}]*', line)[0]
                    time = re.findall('[0-9]*:[0-9]*:[0-9]*', time)[0]
                    x = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_x[^,}]*', line)[0])[0]
                    y = re.findall ('[-0-9]*\.[0-9]*', re.findall('pos_y[^,}]*', line)[0])[0]
                    t['observed_path'].append ( (float (x), float (y), time) )

    # Parse coverage file
    coverageData = []
    fh = args.coverage_file
    with open (fh) as f:
        coverage = f.readlines()
        for line in coverage:
            CSVrow = line.rstrip().split(",")
            coverageData.append (CSVrow)
    # Init 
    timeEllapsed_s = 0

    # Init counters for how many times the entire group is in view
    numIntervalsContainedGroup = 0
    numIntervalsMissingGroup = 0 # While this should be (total - contained), good to make sure they sum correctly


    # Main Evaluation Loop
    for c in coverageData:
        # Get footprint
        footprint = c[0:8]
        footprint = [float (f) for f in footprint]
        print (footprint)
        footprint = [(footprint[0], footprint[1]), (footprint[2], footprint[3]), (footprint[4], footprint[5]), (footprint[6], footprint[7])]
        footprint = Polygon (footprint)
        
        # Get duration of footprint
        footprintDuration = int (c[8])
        timeEllapsed_s = timeEllapsed_s + footprintDuration
        
        # For each target, see how long spent in footprint
        numCheck = footprintDuration

        # Check how long each target in footprint
        # Note: checks entire duration! Because a target could go in and out of view
        for t in targets:
            t['isContainedList'] = []
            numIntervalsContained = 0
            numIntervalsMissing = 0
            for n in range (numCheck):
                if (len (t['observed_path']) > 0):
                    observation = t['observed_path'].pop (0)
                    if (observation == 'A'):
                        if (len (t['observed_path']) > 0):
                            observation = t['observed_path'].pop (0)
                        else:
                            observation = t['waypoints'][len (t['waypoints']) - 1]
                    observation = Point (( float (observation[0]), float (observation[1]) ))
                if (footprint.contains (observation)):
                    numIntervalsContained = numIntervalsContained + 1
                    t['isContainedList'].append (1)
                else:
                    numIntervalsMissing = numIntervalsMissing + 1
                    t['isContainedList'].append (0)
            percentContained = numIntervalsContained / footprintDuration
            print (t['isContainedList'])
        
        # Compare containment status for each time
        for i in range (0,numCheck):
            allContained = True
            for t in targets:
                if (t['isContainedList'][i] < 1):
                     allContained = False
            if (allContained == True):
                numIntervalsContainedGroup = numIntervalsContainedGroup + 1 
            else:
                numIntervalsMissingGroup = numIntervalsMissingGroup + 1

    # Calculate percentage kept in view
    percentContainedGroup = numIntervalsContainedGroup / timeEllapsed_s
    print (percentContainedGroup, len (coverageData))


if __name__ == "__main__":
    main()
 
