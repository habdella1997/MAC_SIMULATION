# class to define the simulation room -> 
# dimensions
# objects -> mirrors, obstacles, corridors, etc
# RF -> AP , UE devices


# Structure -> 
# Setup the room
# Set up the coordinate system ->  AP will be placed in x,y in the room 
# Set up the mirrors -> FOV
# Set up obstacles -> Area of an obstacle. 
# Set up the ue handset

import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
import channel
import math_toolkit
from Objects import UE, AP, mirror

                        # reflect_x          = x_b
                        # reflect_y          = y_b
                        # reflect_slope      = slope
                        # reflect_intercept  = intercept
                        # incident_slope     = incident_slope
                        # incident_intercept = incident_intercept
                        # NLOS = 1

class Reflector:
    def __init__(self, reflect_x, reflect_y, reflect_slope, reflect_intercept, incident_slope, incident_intercept, NLoS):
        self._reflect_x = reflect_x
        self._reflect_y = reflect_y
        self._reflect_slope = reflect_slope
        self._reflect_intercept = reflect_intercept
        self._incident_slope = incident_slope
        self._incident_intercept = incident_intercept
        self._NLoS = NLoS
        self.mirror = None

    # Getter and Setter for reflect_x
    @property
    def reflect_x(self):
        return self._reflect_x

    @reflect_x.setter
    def reflect_x(self, value):
        self._reflect_x = value

    # Getter and Setter for reflect_y
    @property
    def reflect_y(self):
        return self._reflect_y

    @reflect_y.setter
    def reflect_y(self, value):
        self._reflect_y = value

    # Getter and Setter for reflect_slope
    @property
    def reflect_slope(self):
        return self._reflect_slope

    @reflect_slope.setter
    def reflect_slope(self, value):
        self._reflect_slope = value

    # Getter and Setter for reflect_intercept
    @property
    def reflect_intercept(self):
        return self._reflect_intercept

    @reflect_intercept.setter
    def reflect_intercept(self, value):
        self._reflect_intercept = value

    # Getter and Setter for incident_slope
    @property
    def incident_slope(self):
        return self._incident_slope

    @incident_slope.setter
    def incident_slope(self, value):
        self._incident_slope = value

    # Getter and Setter for incident_intercept
    @property
    def incident_intercept(self):
        return self._incident_intercept

    @incident_intercept.setter
    def incident_intercept(self, value):
        self._incident_intercept = value

    # Getter and Setter for NLoS
    @property
    def NLoS(self):
        return self._NLoS

    @NLoS.setter
    def NLoS(self, value):
        self._NLoS = value



class room2:
    def __init__(self, room_l , room_w, room_structure ):
        self.length  = room_l
        self.width   = room_w
        self.room    = room_structure
        self.MIRRORS = {}

    def setup_room(self):
        #for now, keeping room simple. Just a square, no corridors etc etc.
        pass

    def setup_reflectors_in_room(self, mirror):
        if(mirror == None):
            self.MIRRORS = None
            return
        self.MIRRORS = mirror
        for sector in self.MIRRORS:
            for i in range(0,len(self.MIRRORS[sector])):
                self.MIRRORS[sector][i].xCorP1 = self.MIRRORS[sector][i].c_x - self.MIRRORS[sector][i].length/2*math.cos(math.radians(self.MIRRORS[sector][i].angleTilt))
                self.MIRRORS[sector][i].yCorP1 = self.MIRRORS[sector][i].c_y - self.MIRRORS[sector][i].length/2*math.sin(math.radians(self.MIRRORS[sector][i].angleTilt))
                self.MIRRORS[sector][i].xCorP2 = self.MIRRORS[sector][i].c_x + self.MIRRORS[sector][i].length/2*math.cos(math.radians(self.MIRRORS[sector][i].angleTilt))
                self.MIRRORS[sector][i].yCorP2 = self.MIRRORS[sector][i].c_y + self.MIRRORS[sector][i].length/2*math.sin(math.radians(self.MIRRORS[sector][i].angleTilt))

    
    
    def is_facing_ap(x, y, x_mirror, y_mirror, AP): #legacy 
        '''
        Un-tested function, used to check if a mirror is facing towards the Access Point
        '''
        
        # Calculate the angle between the mirror point and AP
        angle_to_ap = math.atan2(AP.y - y_mirror, AP.x - x_mirror)
        angle_to_line = math.atan2(y - y_mirror, x - x_mirror)
        # Check if the angle difference is less than 90 degrees (within the same hemisphere)
        return abs(angle_to_ap - angle_to_line) <= math.pi / 2
    
    def setup_fov_generic(self, AP):
        if(self.MIRRORS == None):
            return
        for sector in self.MIRRORS:
            for i in range(len(self.MIRRORS[sector])):
                # compute the angle of incidence between the endpoint of the mirror, and the AP
                # tan(opposite / adjacent ) = alpha <-
                alpha_i1 = math.atan2(self.MIRRORS[sector][i].yCorP1-AP.y, self.MIRRORS[sector][i].xCorP1 - AP.x)
                alpha_i2 = math.atan2(self.MIRRORS[sector][i].yCorP2-AP.y ,self.MIRRORS[sector][i].xCorP2 - AP.x)

                # compute the slope based on the angle of reflection
                # slope = tan(angle of incident == angle of reflection {no tilt angle})
                # a tilt angle adds 2*tilt difference between orignal reflection with tilted reflection
                # subtractive 2*tilt angle - alpha yeilds the angle between the y_axis (or the normal of the mirror with 0 tilt angle)and the reflection from the tilted mirror
                m_1 = math.tan(2*math.radians(self.MIRRORS[sector][i].angleTilt) - alpha_i1)
                m_2 = math.tan(2*math.radians(self.MIRRORS[sector][i].angleTilt) - alpha_i2)

                # Compute the FOV line coordinates
                fov_1_x = np.linspace(-self.width, self.width, 1000).tolist()
                fov_2_x = np.linspace(-self.width, self.width, 1000).tolist()

                fov_1_y = (m_1 * (np.array(fov_1_x) - self.MIRRORS[sector][i].xCorP1) + self.MIRRORS[sector][i].yCorP1).tolist()
                fov_2_y = (m_2 * (np.array(fov_2_x) - self.MIRRORS[sector][i].xCorP2) + self.MIRRORS[sector][i].yCorP2).tolist()
            
                #Store results
                self.MIRRORS[sector][i].m_1 = m_1
                self.MIRRORS[sector][i].m_2 = m_2  
                self.MIRRORS[sector][i].fov_1_y = fov_1_y
                self.MIRRORS[sector][i].fov_2_y = fov_2_y
                self.MIRRORS[sector][i].fov_1_x = fov_1_x
                self.MIRRORS[sector][i].fov_2_x = fov_2_x
                self.MIRRORS[sector][i].fov_1_y_intercept = fov_1_y[1] - m_1*fov_1_x[1]
                self.MIRRORS[sector][i].fov_2_y_intercept = fov_2_y[1] - m_2*fov_2_x[1]
    


    #Returns Valid Reflection Path Considering AP beamwidth, sector, and mirror
    def setup_valid_reflection_vectors(self,UE, AP, current_sector, mirror):
        reflect_x          = []
        reflect_y          = []
        reflect_slope      = []
        reflect_intercept  = []
        incident_slope     = []
        incident_intercept = []
        NLOS = 0

        x_l = UE.xCor 
        y_l = UE.yCor
        x_o = AP.x 
        y_o = AP.y

        x1 = mirror.xCorP1
        y1 = mirror.yCorP1
        x2 = mirror.xCorP2
        y2 = mirror.yCorP2
        tilt_angle = math.radians(mirror.angleTilt)
        boundary_points = np.linspace(0, 1, 1000)
        reflect_x = 0
        reflect_y = 0
        reflect_slope = 0
        reflect_intercept = 0
        incident_slope = 0
        incident_intercept = 0
        NLOS = 0
        NLoS_Signal = Reflector(reflect_x,reflect_y,reflect_slope,reflect_intercept,incident_slope,incident_intercept,NLOS)
        for s in boundary_points:
            # Compute the boundary point
            x_b = x1 + s * (x2 - x1)
            y_b = y1 + s * (y2 - y1)
            
            # Incident vector from light source to boundary point
            incident_vector = np.array([x_b - x_l, y_b - y_l])
            incident_vector = incident_vector / np.linalg.norm(incident_vector)  # Normalize
            
            incident_slope     = (y_b - y_l) /(x_b - x_l)
            incident_intercept = y_l - (incident_slope*x_l)
            # Mirror normal vector at the boundary point
            mirror_normal = np.array([-1 * np.sin(tilt_angle), np.cos(tilt_angle)])
            # Reflection using the law of reflection
            reflection_vector = incident_vector - 2 * np.dot(incident_vector, mirror_normal) * mirror_normal

            # dot_product = np.dot(reflection_vector, mirror_normal)
            # reflection_angle = np.degrees(np.arccos(dot_product / (np.linalg.norm(reflection_vector) * np.linalg.norm(mirror_normal))))

            # if dot_product < 0 or reflection_angle > 90:
            #     return None  # Skip this boundary point
            # Compute the slope of the reflected ray
           
            if reflection_vector[0] != 0:  # Ensure no division by zero
                slope = reflection_vector[1] / reflection_vector[0]
            else:
                slope = np.inf  # Vertical line
            # Line equation of the reflected ray: y = slope * x + intercept
            intercept = y_b - slope * x_b
            
            #sector Vector
            left_vector  = (AP.sector_leftBoundary[current_sector][0] , AP.sector_leftBoundary[current_sector][1])
            right_vector = (AP.sector_rightBoundary[current_sector][0] , AP.sector_rightBoundary[current_sector][1])
            end_1 = -1 if AP.sector_leftBoundary[current_sector][2] > 180 else 1
            end_2 = -1 if AP.sector_rightBoundary[current_sector][2] > 180 else 1
            
            slope_left,intercept_left = math_toolkit.convert_vector_to_slope(left_vector, 
                                                                            (AP.x, AP.y),
                                                                            100, 
                                                                            0, end_1 * self.length)
            slope_right,intercept_right = math_toolkit.convert_vector_to_slope(right_vector, 
                                                                            (AP.x, AP.y),
                                                                            100, 
                                                                            0, end_1 * self.length)
            
            if(slope_left == None):
                degree_org = AP.sector_leftBoundary[int(current_sector)][2] + 1
                left_vector  = (round(math.sin(math.radians(degree_org)),7) , 
                              round(math.cos(math.radians(degree_org)),7) )
                slope_left,intercept_left = math_toolkit.convert_vector_to_slope(left_vector, 
                                                                            (AP.x, AP.y),
                                                                            100, 
                                                                             0, end_1 * self.length)
            if(slope_right == None):
                degree_org = AP.sector_rightBoundary[int(current_sector)][2] -2 
                right_vector  = (round(math.sin(math.radians(degree_org)),7) , 
                              round(math.cos(math.radians(degree_org)),7) )
                slope_right,intercept_left = math_toolkit.convert_vector_to_slope(right_vector, 
                                                                            (AP.x, AP.y),
                                                                            100, 
                                                                             0, end_1 * self.length)
            # print("slope left: " + str(slope_left) )
            # print("Slope right: " + str(slope_right))
            # print("reflected slope: "  +str(slope))
            valid_reflection = False
            if(slope != np.inf and slope_left!= None and slope_right!=None):
                if(slope_left <= slope_right):
                    valid_reflection = slope_left <= slope <= slope_right
                else:
                    valid_reflection = slope <= slope_left and slope >= slope_right
            else:
                valid_reflection = False
            # angle = math.degrees(math.atan2(reflection_vector[0], reflection_vector[1]))
            # if angle < 0:
            #     angle += 360  # Wrap to [0, 360]
    
            # print("Angle Computed: " + str(angle))
            # print("Left Boundary : " + str(AP.sector_leftBoundary[int(current_sector)][2]))
            # print("Right Boundary : " + str(AP.sector_rightBoundary[int(current_sector)][2]))
            # print("Sector: " + str(current_sector))
            # return None
            # if slope != np.inf and (AP.sector_leftBoundary[int(current_sector)][2]<= angle <= AP.sector_rightBoundary[int(current_sector)][2]):
            if slope != np.inf and (valid_reflection):
                y_at_observer = slope * x_o + intercept
                if np.isclose(y_at_observer, y_o, atol=1):
                    if(NLOS <= 0 or abs(y_at_observer) < abs(reflect_intercept)  ):
                        reflect_x          = x_b
                        reflect_y          = y_b
                        reflect_slope      = slope
                        reflect_intercept  = intercept
                        incident_slope     = incident_slope
                        incident_intercept = incident_intercept
                        NLOS = 1
                        # print("ue_device pass: " + str(UE.id))
                        #elseif is wrong, it takes the next point. fix later
                    elif(abs(y_at_observer) >= abs(reflect_intercept) and NLOS==1):
                        NLoS_Signal.reflect_x          = reflect_x
                        NLoS_Signal.reflect_y          = reflect_y
                        NLoS_Signal.reflect_slope      = reflect_slope
                        NLoS_Signal.reflect_intercept  = reflect_intercept
                        NLoS_Signal.incident_slope     = incident_slope
                        NLoS_Signal.incident_intercept = incident_intercept
                        NLoS_Signal.NLoS = 1
                        NLoS_Signal.mirror = mirror
                        break      
            elif slope == np.inf and (AP.sector_leftBoundary[int(current_sector)][2]<=360-math.degrees(math.atan(slope)) <= AP.sector_rightBoundary[int(current_sector)][2]):
                print("Vertical Line Criteria Met But Not Handled -> Throwing ERROR")
                sys.exit(1)
            else:
                continue
        return NLoS_Signal
    
    def getUESector(self, UE, AP): #Finds in which sector the UE is currenty sitting in. If the UE is mobile, it will have to update its X,Y coordiantes before calling this function
            x = UE.xCor
            y = UE.yCor
            ueAngle = math.degrees(math.atan2(x,y))  #relative to the y axis
            if(ueAngle < 0):
                ueAngle += 360
            for i in range(0,AP.number_of_sectors):
                left_boundary = AP.sector_leftBoundary[i][2]
                right_boundary = AP.sector_rightBoundary[i][2]
                if(ueAngle >= left_boundary and ueAngle < right_boundary):
                    return AP.sector_map[i]
                else:
                    continue
            print("ERROR Fatal - UE is in no Sector")
            sys.exit(1)
            return

    # Function used to find the mirrors in the room in which the UE is of its field of view. 
    def mirrors_with_coverage(self,UE,currentSector):
        mirrors_UEFoV_Pass = [] #holds the mirrors the satistfy the condition of UE coordinates are bounded by the mirror FoV
        mirrors_in_this_sector = self.MIRRORS[currentSector]
        for i in range(0,len(mirrors_in_this_sector)): 

            slope_1   = mirrors_in_this_sector[i].m_1
            slope_2   = mirrors_in_this_sector[i].m_2
            y_int_1   = mirrors_in_this_sector[i].fov_1_y_intercept
            y_int_2   = mirrors_in_this_sector[i].fov_2_y_intercept

            x_1 = (UE.yCor - y_int_1 ) / slope_1
            x_2 = (UE.yCor - y_int_2 ) / slope_2
 
            if(x_1<x_2 and UE.xCor <= x_2 and UE.xCor >= x_1):
                mirrors_UEFoV_Pass.append(mirrors_in_this_sector[i])
            elif(x_2<x_1 and UE.xCor <= x_1 and UE.xCor >= x_2):
                mirrors_UEFoV_Pass.append(mirrors_in_this_sector[i])
            else:
                continue
        return mirrors_UEFoV_Pass
    
    # def plot_NLoS_Signal(self,NLoSSignal:Reflector):

    def setup_all_reflection_vectors(self,ueDevice, AP,currentSector, custom_single_link_per_plot = False, index_mirror = -1):
        x_l = ueDevice.xCor 
        y_l = ueDevice.yCor
        x_o = AP.x 
        y_o = AP.y
        my_mirrors_for_every_sector = []
        # for i in range(0,AP.number_of_sectors):
        my_mirrors = self.mirrors_with_coverage(ueDevice,currentSector)
        # my_mirrors_for_every_sector += my_mirrors
        # my_mirrors = self.MIRRORS[10]
        NLoS_Signals = []
        if(custom_single_link_per_plot):
            my_mirrors = [self.MIRRORS[index_mirror]]
        for i in range(len(my_mirrors)):
            if(len(NLoS_Signals) >= 1 and NLoS_Signals[0]!= None):
                return NLoS_Signals[0]
                
            mirror = my_mirrors[i]
            x1 = my_mirrors[i].xCorP1
            y1 = my_mirrors[i].yCorP1
            x2 = my_mirrors[i].xCorP2
            y2 = my_mirrors[i].yCorP2
            tilt_angle = math.radians(my_mirrors[i].angleTilt)
            boundary_points = np.linspace(0, 1, 1000)
            reflect_x=0
            reflect_y=0
            reflect_slope=0
            reflect_intercept=0
            incident_slope=0
            incident_intercept=0
            self_NLOS = 0
            NLoS_Signal = Reflector(reflect_x,reflect_y,reflect_slope,reflect_intercept,incident_slope,incident_intercept,self_NLOS)
            for s in boundary_points:
                # Compute the boundary point
                x_b = x1 + s * (x2 - x1)
                y_b = y1 + s * (y2 - y1)
                
                # Incident vector from light source to boundary point
                incident_vector = np.array([x_b - x_l, y_b - y_l])
                incident_vector = incident_vector / np.linalg.norm(incident_vector)  # Normalize
                
                incident_slope     = (y_b - y_l) /(x_b - x_l)
                incident_intercept = y_l - (incident_slope*x_l)
                # Mirror normal vector at the boundary point
                mirror_normal = np.array([-1 * np.sin(tilt_angle), np.cos(tilt_angle)])
                
                # Reflection using the law of reflection
                reflection_vector = incident_vector - 2 * np.dot(incident_vector, mirror_normal) * mirror_normal
  
                if reflection_vector[0] != 0:  # Ensure no division by zero
                    slope = reflection_vector[1] / reflection_vector[0]
                else:
                    slope = np.inf  # Vertical line
                
                # Line equation of the reflected ray: y = slope * x + intercept
                intercept = y_b - slope * x_b
                # Check if the reflected ray intersects the observer
     
                if slope != np.inf:
                    y_at_observer = slope * x_o + intercept
                    if np.isclose(y_at_observer, y_o, atol=1):
                        if(self_NLOS<=0 or abs(y_at_observer) < abs(reflect_intercept)  ):
                            reflect_x=x_b
                            reflect_y=y_b
                            reflect_slope=slope
                            reflect_intercept=intercept
                            incident_slope=incident_slope
                            incident_intercept=incident_intercept
                            self_NLOS = 1
                            #elseif is wrong, it takes the next point. fix later
                        elif(abs(y_at_observer) >= abs(reflect_intercept) and self_NLOS==1):
                            NLoS_Signal.reflect_x          = reflect_x
                            NLoS_Signal.reflect_y          = reflect_y
                            NLoS_Signal.reflect_slope      = reflect_slope
                            NLoS_Signal.reflect_intercept  = reflect_intercept
                            NLoS_Signal.incident_slope     = incident_slope
                            NLoS_Signal.incident_intercept = incident_intercept
                            NLoS_Signal.NLoS = 1
                            NLoS_Signals.append(NLoS_Signal)
                            break      
                elif slope == np.inf :
                    # Special case: vertical line, check if x_b matches x_o
                    if np.isclose(x_b, x_o, atol=1):
                        print("ERROr -slope - inf")
                        sys.exit(1)
                        # print(f"Vertical ray intersects at ({x_b:.2f}, {y_b:.2f})")
                        # UE[0].reflect_x = x_b
                        # UE[0].reflect_y = y_b
                        # UE[0].reflect_slope = slope
                        # UE[0].reflect_intercept = intercept
                        # UE[0].NLOS = 1
                        return
                else:
                    continue
        return NLoS_Signals


        