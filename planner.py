import math

# Type of planner
POINT_PLANNER=0; TRAJECTORY_PLANNER=1



class planner:
    def __init__(self, type_):

        self.type=type_

    
    def plan(self, goalPoint=[-1.0, -1.0]):
        
        if self.type==POINT_PLANNER:
            return self.point_planner(goalPoint)
        
        elif self.type==TRAJECTORY_PLANNER:
            return self.trajectory_planner()


    def point_planner(self, goalPoint):
        x = goalPoint[0]
        y = goalPoint[1]
        return x, y

    # TODO Part 6: Implement the trajectories here
    def trajectory_planner(self):
        # Generate trajectory points for both parabola and sigmoid
    
        # Parabola: y = x^2 for x ∈ [0.0, 1.5]
        parabola_points = []
        x_start, x_end = 0, -1.5
        num_points = 30  # Adjust density as needed
    
        for i in range(num_points + 1):
            x = x_start + (x_end - x_start) * i / num_points
            y = x * x
            parabola_points.append([x, -y])
    
        # Sigmoid: σ(x) = 2/(1 + e^(-2x)) - 1 for x ∈ [0.0, 2.5]
        sigmoid_points = []
        x_start, x_end = -0.5, 0.5
    
        for i in range(num_points + 1):
            x = x_start + (x_end - x_start) * i / num_points
            y = 2.0 / (1.0 + math.exp(-2.0 * x)) - 1.0
            sigmoid_points.append([x-0.5, y-0.462])
    
        # return parabola_points
        return sigmoid_points

