import math
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
import channel
class room:
    def __init__(self, room_l , room_w, room_structure ):
        self.length = room_l
        self.width = room_w
        self.room = room_structure

    def setup_reflectors_in_room(self, mirror, num_mirrors):
        for i in range(0,num_mirrors):
            mirror[i].xCorP1 = mirror[i].c_x - mirror[i].length/2*math.cos(math.radians(mirror[i].angleTilt))
            mirror[i].yCorP1 = mirror[i].c_y - mirror[i].length/2*math.sin(math.radians(mirror[i].angleTilt))
            mirror[i].xCorP2 = mirror[i].c_x + mirror[i].length/2*math.cos(math.radians(mirror[i].angleTilt))
            mirror[i].yCorP2 = mirror[i].c_y + mirror[i].length/2*math.sin(math.radians(mirror[i].angleTilt))

    
    def print_mirror_coordinates(self,mirror,num_mirror):
        for i in range(num_mirror):
            print("Mirror " + str(i) +" P1 Coordinates: \n")
            print("(" + str(mirror[i].xCorP1) + "," + str(mirror[i].yCorP1) + ")\n")
            print("Mirror " + str(i) + " P2 Coordinates: \n")
            print("(" + str(mirror[i].xCorP2) + "," + str(mirror[i].yCorP2) + ")\n")
    
    def is_facing_ap(x, y, x_mirror, y_mirror):
    # Calculate the angle between the mirror point and AP
        angle_to_ap = math.atan2(0 - y_mirror, 0 - x_mirror)
        angle_to_line = math.atan2(y - y_mirror, x - x_mirror)
        
        # Check if the angle difference is less than 90 degrees (within the same hemisphere)
        return abs(angle_to_ap - angle_to_line) <= math.pi / 2
    
    def setup_fov_generic(self, mirror,num_mirrors):
        #compute mirror end points.
        for i in range(num_mirrors):
            alpha_i1 = math.atan2(mirror[i].yCorP1 , mirror[i].xCorP1)
            alpha_i2 = math.atan2(mirror[i].yCorP2 , mirror[i].xCorP2)

            m_1 = math.tan(2*math.radians(mirror[i].angleTilt) - alpha_i1)
            m_2 = math.tan(2*math.radians(mirror[i].angleTilt) - alpha_i2)

            fov_1_x = np.linspace(-self.width, self.width, 1000).tolist()
            fov_2_x = np.linspace(-self.width, self.width, 1000).tolist()

            fov_1_y = (m_1 * (np.array(fov_1_x) - mirror[i].xCorP1) + mirror[i].yCorP1).tolist()
            fov_2_y = (m_2 * (np.array(fov_2_x) - mirror[i].xCorP2) + mirror[i].yCorP2).tolist()
           
            fov_1_y_clean = []
            fov_2_y_clean = []
            fov_1_x_clean = []
            fov_2_x_clean = []
            

            for x, y in zip(fov_1_x, fov_1_y):
                if room.is_facing_ap(x, y, mirror[i].xCorP1, mirror[i].yCorP1):
                    fov_1_x_clean.append(x)
                    fov_1_y_clean.append(y)

            for x, y in zip(fov_2_x, fov_2_y):
                if room.is_facing_ap(x, y, mirror[i].xCorP2, mirror[i].yCorP2):
                    fov_2_x_clean.append(x)
                    fov_2_y_clean.append(y)


            mirror[i].m_1 = m_1
            mirror[i].m_2 = m_2 
            mirror[i].fov_1_y = fov_1_y_clean
            mirror[i].fov_2_y = fov_2_y_clean
            mirror[i].fov_1_x = fov_1_x_clean
            mirror[i].fov_2_x = fov_2_x_clean
            mirror[i].fov_1_y_intercept = fov_1_y[1] - m_1*fov_1_x[1]
            mirror[i].fov_2_y_intercept = fov_2_y[1] - m_2*fov_2_x[1]
    
    
        