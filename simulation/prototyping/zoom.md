# Summary
Zooming should be preferable over moving the UAV whenever possible because it is less expensive. Therefore, the
zoom capability needs to be available and a status needs to be set

## possible class
### I included some code from Aruns pseudo example and I am writing in c++ because I have the most experience in this

  class camera
      float currentZoomLvl, maxZoomLvl, minZoomLvl; //Zoom levels
      float moveCamera[3]; //[0]= move fwd/ backwards, [1]=left/right, [2]=up/down
      float yaw_delta;  //(rotation about z axis)

      int standoff;   //standoff distance
      int speed ;     // more the distance, faster should go
      int tilt;       //gimbal tilt up down (angle range)

    public:    
      float getZoomLvl() return currentZoomLvl;
      float calcZoom(float targetAposition[3], targetBposition[3], robotPosition[3]){
        // take positions and create
      }

## When to zoom?

  - where are the UAVS in relation to each other and myself?
  - As they get further apart I need to zoom out.
  - As they get closer together I need to zoom in.
  - As I get futher away I need to zoom in.
  - As I get closer I need to zoom out.


## How much to zoom?
  - I should probably make it proportional to the degree of distance between the USVs
  or/and
  - I should make it proportional to the distance between myself and the central point of calculation

## How does that change with orientation?
  - If we are tilting to account for distance then we should avoid zooming to create consistent image quality
  - If we are going to operate outside of the centroid then the zoom will need to change
