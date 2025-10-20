from math import atan2, asin, sqrt

M_PI=3.1415926535

class Logger:
    
    def __init__(self, filename, headers=["e", "e_dot", "e_int", "stamp"]):
        
        self.filename = filename

        with open(self.filename, 'w') as file:
            
            header_str=""

            for header in headers:
                header_str+=header
                header_str+=", "
            
            header_str+="\n"
            
            file.write(header_str)


    def log_values(self, values_list):

        with open(self.filename, 'a') as file:
            
            vals_str=""
            
            for value in values_list:
                vals_str+=f"{value}, "
            
            vals_str+="\n"
            
            file.write(vals_str)
            

    def save_log(self):
        pass

class FileReader:
    def __init__(self, filename):
        
        self.filename = filename
        
        
    def read_file(self):
        
        read_headers=False

        table=[]
        headers=[]
        with open(self.filename, 'r') as file:

            if not read_headers:
                for line in file:
                    values=line.strip().split(',')

                    for val in values:
                        if val=='':
                            break
                        headers.append(val.strip())

                    read_headers=True
                    break
            
            next(file)
            
            # Read each line and extract values
            for line in file:
                values = line.strip().split(',')
                
                row=[]                
                
                for val in values:
                    if val=='':
                        break
                    row.append(float(val.strip()))

                table.append(row)
        
        return headers, table
    
    

def euler_from_quaternion(quat):
    """
    Convert quaternion (w in last place) to euler roll, pitch, yaw.
    quat = [x, y, z, w]
    """
    # just unpack yaw because yaw is z, which is the only thing we are tracking
    x = quat.x
    y = quat.y
    z = quat.z
    w = quat.w
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = atan2(siny_cosp, cosy_cosp)

    return yaw # in radians

def calculate_linear_error(current_pose, goal_pose):
    # Compute the linear error in x and y
    # Remember that current_pose = [x,y, theta, time stamp] and goal_pose = [x,y]
    # Remember to use the Euclidean distance to calculate the error.
    curr_x = current_pose[0]
    curr_y = current_pose[1]
    goal_x = goal_pose[0]
    goal_y = goal_pose[1]
    error_linear = sqrt(pow(goal_x - curr_x, 2) + pow(goal_y - curr_y, 2))

    return error_linear

def calculate_angular_error(current_pose, goal_pose):
    # Remember that current_pose = [x,y, theta, time stamp] and goal_pose = [x,y]
    # Use atan2 to find the desired orientation
    # Remember that this function returns the difference in orientation between 
    # where the robot currently faces and where it should face to reach the goal
    curr_theta = current_pose[2]
    dx = goal_pose[0] - current_pose[0]
    dy = goal_pose[1] - current_pose[1]

    desired_yaw = atan2(dy, dx)
    error_angular = desired_yaw - curr_theta

    # Remember to handle the cases where the angular error might exceed the range [-π, π]
    while error_angular > M_PI:
        error_angular -= 2.0 * M_PI
    while error_angular < -M_PI:
        error_angular += 2.0 * M_PI

    return error_angular