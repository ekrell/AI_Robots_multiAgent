## Literature Review: Notes

_Keeping Multiple Moving Targets in the Field of View of a Mobile Camera_

Nicholas R. Gans, Guoqiang Hu, Kaushik Nagarajan, and Warren E. Dixon

2011


The authors used image processing to determine the postions and velocities of targets at any given moment. 
They did not have information regarding goal or trajectory. They simply used the state at any time. 
They did not use any models/learning to predict future states. 
They kept the targets in FOV by maintaining two properties: 

		1. Mean target position is in middle of FOV     - keeps most in FOV
		2. Variance of target position is low           - Keeps most from straying into edges 

Since they have positions and velocities of targets, they determine what position and velocity the camera should be set to in order to maintain the properties. 

With our project, the actual positions are simply given to us. Also, this robot camera is following behind and is sitatued underneat the targets in the Z-coord. 
So a very different scenaria, but the idea of using functions where we take what we know to solve for a position and velocity that maintains properties is interesting.
Also the idea of minimizing variance and keeping the mean in the middle of FOV could be useful for ours for a stable image. 
