## Robot Behavior Document
# Robot: QCOORD


@startuml

title QCOORD quadcopter behaviors

package "Follow Targets" {
component [GCS] #AliceBlue

component [Waypoint] #fff0f0

component [locate_centroid] #f7f7f7
component [follow] #f7f7f7

[GCS] -> [locate_centroid] : coordinates_of_targets
[locate_centroid] -> [follow] : vector_to_centroid
[follow] -> [Waypoint] : vector_to_follow_position
}

package "Keep Targets in Camera View" {
component [Altitude_Control] #fff0f0
component [adjust_view_altitude] #f7f7f7
[GCS] -> [adjust_view_altitude] : coordinates_of_targets
[adjust_view_altitude] -> [Altitude_Control] : altitude
}

@enduml 



 
