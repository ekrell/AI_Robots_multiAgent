
## Pseudocode: PathPrediction


**Main:**

	Initialize each target's previous position to None

	Initialize each target's speed to 0

	Get current positions for each target

	Initialize centroid's previous position to None

	Calculate current centroid position

	Set Predict equal to True

	While Predict is True

		Update the target's positions

		If unable to update the target's positions

			Set Predict equal to False

			Break out of loop

		Estimate target speed using (distance) / (time)

		Update the centroid position using the current target positions

		Call 'predictPath': Predict each target's sequence of predicted future positions

		Call 'calcCentroidPath': Use the Paths to predict the positions of the centroid

	Output the target and centroid paths



**predictPath:**

INPUTS:

- Targets: Target objects

OUTPUTS:
	
- Predicted paths for each Target


	Initialize Paths to store each target's predicted path points

	For each target:


		Set p as target's current position

		Set the first element of the path to p (starting location)

		Set w is current waypoint

		Set s as the current position (source point)

		While there are still waypoints:

			Set Theta as the angle between w and the x-axis		

			Set ThetaPrime as the angle between p and the x-axis

			Calculate the (x, y) velocity components using 
			( X-velocity = cosine (ThetaPrime) * target speed,
			Y-velocity = sine (ThetaPrime) * target speed )

			Set interval vector i with distance that would be traveled in the time interval using
			(X-velocity * timeInterval, Y-velocity * timeInterval)

			Calculate the magnitude of i using hypotenuse of the components

			Rotate the interval vector toward the waypoint by calculating the
			components of a vector whose magnitude is equal to i's and whose
			angle is equal to w's 

			Set p as the vector addition of p and i (extend p in direction of w)

			Add p to target's Path

			Calculate the distance from source point to waypoint w

			Calculate the distance from source point to current predicted point p 

			If p is further away than the waypoint:

				Set w as the next waypoint, since w has been reached

				Set s as previous waypoint, which is now the source point
			
	Return Paths


**calcCentroidPath:**

INPUTS:

- Paths: predicted paths for each target
- Targets: Target objects

OUTPUTS:
- Predicted path of the centroid


	Initialize empty centroid path

	Set lenmax as the longest target path

	For i in range 0 to lenmax:

		Set State as each target's point at the current interval. 
		(Some targets may reach their final waypoints first, so their final points repeat as they are stationary)

		Calculate the centroid position using the points

		Append this centroid position to the predicted path

	Return the centroid paths


