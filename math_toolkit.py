import bisect
import random
import math 
import scipy.special as sp
import numpy as np
import sys


#new generator -> Node Density

def randomCoordinates(expected_nodes,radius):
    # Generate random polar coordinates
    theta = np.random.uniform(0, 2 * np.pi, expected_nodes)  # Angle
    r_values = radius * np.sqrt(np.random.uniform(0, 1, expected_nodes))  # Distance

    # Convert to Cartesian coordinates
    x_coords = r_values * np.cos(theta)
    y_coords = r_values * np.sin(theta)
    # Displaying UEs coordinates
    ue_coordinates = list(zip(x_coords, y_coords))
    return ue_coordinates



# New Generator -> transmission
def generate_transmission_times(lambda_rate, start_time,end_time):
    transmission_times = []
    current_time = start_time

    # Generate transmission times up until end_time
    while current_time < end_time:
        # Generate the next inter-arrival time
        random_time = np.random.exponential(lambda_rate)
        current_time += random_time

        # Ensure only one transmission per cycle
        if current_time < end_time:
            transmission_times.append((current_time))
    return transmission_times







#Between Two Points using a Poisson Distribution
def random_generator(point_A , point_B, lambda_):
    list = []
    while True:
        u = random.uniform(0,1)
        time_advance = -1 * (1/lambda_) * math.log(1-u)
        if ( len(list) == 0 ):
            if(time_advance < point_B):
                list.append((time_advance))
            else:
                print("Error Math Toolkit (Random Generator): point_B is too small")
                exit
        else:
            insert_value = (list[-1] + time_advance)
            if(insert_value < point_B):
                if(insert_value == list[len(list)-1]):
                    list.append(insert_value+1)
                else:
                    list.append(insert_value)
            else:
                break
    if(list[len(list)-1] > point_B):
        list.pop(list[len(list)-1])
    return list

def random_XY_coordinates(x_boundary , y_boundary):
    xCor = random.randint(-1*x_boundary, x_boundary)
    yCor = random.randint(-1*y_boundary, y_boundary)
    return xCor, yCor 

def random_uniform_between(leftbound, rightbound):
    return random.uniform(leftbound, rightbound)

#Binary Search
def binary_search(sorted_list, target):
    left, right = 0, len(sorted_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return True  # Target found
        elif sorted_list[mid] < target:
            left = mid + 1  # Target is in the right half
        else:
            right = mid - 1  # Target is in the left half
    return False  # Target not found 


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def Q_function(x):
    return 0.5 * sp.erfc(x / math.sqrt(2))

def create_line(slope,intercept, num_points, start, end):
    x = np.linspace(start, end, num_points).tolist()
    y = []
    if(slope == None): # vertical line
        return x,None
    for i in range(len(x)):
        y.append(slope*x[i] + intercept)
    return x,y

def convert_vector_to_line(direction_vector, start_point,num_points, start, end):
    slope,intercept = cartesian_line(start_point, direction_vector)
    return create_line(slope,intercept,num_points,start,end)

def convert_vector_to_slope(direction_vector, start_point,num_points, start, end):
    slope,intercept = cartesian_line(start_point, direction_vector)
    return slope,intercept

def cartesian_line(start_point, direction_vector):
    """
    Converts parametric line to Cartesian form y = mx + b if possible.
    
    Parameters:
    start_point (tuple): A point on the line (x0, y0)
    direction_vector (tuple): The direction of the line (vx, vy)
    
    Returns:
    tuple: Slope (m) and intercept (b) of the line if it can be converted.
           Returns None if the line is vertical (undefined slope).
    """
    x0, y0 = start_point
    vx, vy = direction_vector

    # Check for vertical line where slope is undefined
    if (vx-x0) == 0:
        return None,None
    m = (vy-y0) / (vx-x0)
    b = y0 - m * x0
    return m, b

def find_index(lst, num):
    try:
        return lst.index(num)
    except ValueError:
        return None


def shuffle_list(list):
    return random.shuffle(list)

    



        