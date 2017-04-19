The following describes the Follow_Targets() inputs, outputs, and a simple command line interface specification used with the Morse simulator.
Such an interface easily ports to a Mission Planner script. It also could be used within a larger system (such as a subsumption architecture) where attribute parameters are dynamically updated by other autonomous behaviors. 

__Arguments:__

- -n: Name or connection string of the following quadcopter
- -f: File containing quadcopter attributes, such as maximum and minimum speeds, pre-selected targets, etc

__Command Line Interface:__

    TRACK                           Enable tracking behavior
    PAUSE                           Stop following, but continue communication with targets and path prediction
    HALT                            Terminate tracking behavior
    ADD TARGETS <target 1> <target 2> ... <target N>        Add targets to track
    DEL TARGETS <target 2> <target 2> ... <target N>        Delete targets to track
    SET <attribute> <value>         Modify attributes, such as minimum and maximum speeds
    GET <attribute>                 Display attribute value
    CLEAR <attribute>               Sets attribute to default/file value
    CLEAR-ALL                       Sets all attributes to default/file values
    SYSCHECK                        Perform a system status check, ensures all sensors and actuators online

__Parameters:__

Minimum speed
Maximum speed
Minimum tilt angle
Maximum tilt angle
Minimum zoom level
Maximum zoom level

__Outputs:__

Quadcopter's basic state values are periodically output to a log file. 
Each row is comma-separated such that the full log file is a CSV, 
easily visualized using R or Excel/Calc. 

The prediction data varies widely in length is thus less suitable for CSV.
Each prediction is an ordered list of 2-tuples with (x, y) coordinates. 
There are predictions for each Target's path as well as one collective centroid path.
Each target's predictions are logged in that target's file. The centroid gets its own file. 
Note that each element of a prediction is separated temporally by a time interval. 
The timing for a sequence can be reconstructed since the prediction is logged along with a timestamp corresponding the first element. 
