import Objects.mirror as mirror
import numpy as np
import math
import math_toolkit
import Objects.mirror as mirror
import Objects.room
import sys
import Objects.AP as AP
import channel
from collections import deque
import RF
from Objects.transmission2 import UL_DATA

class UETransmission:
    
    Failed_MSG1 = "No NLoS Link Available at time: "
    Failed_MSG2 = "No LoS Link Available at time: "
    Failed_MSG3 = "Link Available, but colloision occured: "
    Failed_MSG4 = "Link Could not be closed: SNR Threshold Not Met"
    Failed_MSG5 = "Failure Unknown - Debug Needed"

    def __init__(self, max_reTransmissions):
        self._transmission_time = deque()
        self._transmission_time_record = []
        self.transmission_IDList = [] #Generates a internal id for every application layer transmission instance to track packets

        self.Logs_ActualTransmissionTime = []
        self.Logs_AppTransmissionTime    = []
        self.Logs_ULSeqID                = []
        self.Logs_AppSeqID               = []
        self.Logs_LinkType               = []
        self.Logs_NumTransmissions       = []
        self.Logs_Status                 = []
        self.Logs_APSector               = []

        self.pending_transmission_SeqID   = [] # holds the pending internal APP layer UL ID
        self.pending_transmission_AppTime = [] # holds the pending internal APP layer UL transmission time
        self.pending_transmission_ULPacket = [] # holds the pending global UL Packet 
        
        self.numberOfReTransmissions = None

    def set_transmission_time(self, time):
        self._transmission_time        = deque(time) #Every time a transmission occurs we pop the left most item. 
        self._transmission_time_record = time # Remains un-altered throughout the simulation.
        APPSeqIDLIST                   = [x for x in range(len(time))]
        self.transmission_IDList = deque(APPSeqIDLIST)
        self.numberOfReTransmissions = {key: 0 for key in APPSeqIDLIST}
    
    def check_earliest_transmission(self):
        return self._transmission_time[0]
    
    def empty(self):
        if(len(self._transmission_time) >0 ):
            return False
        return True
    
    def transmit_failure(self,ulPacketSequencID,linkType,APSector):
        match = -1
        for index,ul_packet in enumerate(self.pending_transmission_ULPacket):
            if(ul_packet.sequence_id == ulPacketSequencID):
                match = index
        if(match == -1):
            print("seq id " + str(ulPacketSequencID))
            for ul_packet in (self.pending_transmission_ULPacket):
                print(ul_packet.sequence_id + print(", "))
            print("Processing a Failed Transmission Failed. UL Packet does not exist anymore <Two Failures - look at you>")
            sys.exit(1)

        
        self.Logs_AppTransmissionTime.append(self.pending_transmission_AppTime[match])
        self.Logs_ActualTransmissionTime.append(self.pending_transmission_ULPacket[match].timeStampTransmission)
        self.Logs_ULSeqID.append(self.pending_transmission_ULPacket[match].sequence_id)
        self.Logs_AppSeqID.append(self.pending_transmission_SeqID[match])
        self.Logs_LinkType.append(linkType)
        self.Logs_NumTransmissions.append(self.numberOfReTransmissions[self.pending_transmission_SeqID[match]])
        self.Logs_Status.append("Fail")
        self.Logs_APSector.append(APSector)
        
        self.numberOfReTransmissions[self.pending_transmission_SeqID[match]] +=1
        
        APP_time = self.pending_transmission_AppTime.pop(match)
        SEQ_ID   = self.pending_transmission_SeqID.pop(match)
        self.pending_transmission_ULPacket.pop(match)
        
        match = -2

        for index,time in enumerate(self._transmission_time):
            if(time >= APP_time):
                match = index-1
                break
        
        if(index == -1):
            self._transmission_time.appendleft(APP_time)
            self.transmission_IDList.appendleft(SEQ_ID)
        elif(index == -2):
            self._transmission_time.append(APP_time)
            self.transmission_IDList.append(SEQ_ID)
        else:
            self._transmission_time.insert(match,APP_time)
            self.transmission_IDList.insert(match,SEQ_ID)
        



    def transmit_success(self, ulPacketSequencID,APSector):
        match = -1
        ul_packet = None
        for index,ul_packet in enumerate(self.pending_transmission_ULPacket):
            if(ul_packet.sequence_id == ulPacketSequencID):
                match = index
                ul_packet = ul_packet
        if(match == -1):
            print("Processing a Successful Transmission Failed. UL Packet does not exist anymore")
            sys.exit(1)
        
        self.Logs_AppTransmissionTime.append(self.pending_transmission_AppTime[match])
        self.Logs_ActualTransmissionTime.append(self.pending_transmission_ULPacket[match].timeStampTransmission)
        self.Logs_ULSeqID.append(self.pending_transmission_ULPacket[match].sequence_id)
        self.Logs_AppSeqID.append(self.pending_transmission_SeqID[match])
        self.Logs_LinkType.append(self.pending_transmission_ULPacket[match].linkType)
        self.Logs_NumTransmissions.append(self.numberOfReTransmissions[self.pending_transmission_SeqID[match]])
        self.Logs_Status.append("Pass")
        self.Logs_APSector.append(APSector)

        intial_time = self.pending_transmission_AppTime[match]
        
        self.pending_transmission_AppTime.pop(match)
        self.pending_transmission_SeqID.pop(match)
        self.pending_transmission_ULPacket.pop(match)

        return intial_time,ul_packet

    def pending_transmission(self, ULPacket):
        APPTransTime, APPSeqID =  self._transmission_time.popleft(), self.transmission_IDList.popleft()
        self.pending_transmission_SeqID.append(APPSeqID)
        self.pending_transmission_AppTime.append(APPTransTime)
        self.pending_transmission_ULPacket.append(ULPacket)

    @property
    def transmission_time(self):
        return list(self._transmission_time)  # return as a list for easier access

    @property
    def transmission_time_record(self):
        return self._transmission_time_record




class UE: 
    UE_ID = 1 # 0 is taken by AP
    def __init__(self, xCor, yCor, max_reTransmissions, RFBox, transmission_rate, startTime,endTime):
        self.xCor      = xCor
        self.yCor      = yCor
        self.AP        = None
        self.id        = UE.UE_ID
        self.UE_TRANSMISSIONS         = UETransmission(max_reTransmissions)
        self.RFBox  = RFBox
        UE.UE_ID = UE.UE_ID + 1
        self.transmission_rate = transmission_rate
        self.simEndTime        = endTime
        self.startTime         = startTime
        self.mySector = -1
        self.distanceToAP = -1
        self.propagationDelay = -1
    
    def check_number_packets(self,endTime):
        #Function to check how many packets can be transmitted before a certain time instant. 
        UL_Requests_pending = self.UE_TRANSMISSIONS.transmission_time
        time_instances = []
        for pending_time in UL_Requests_pending:
            if pending_time <= endTime:
                time_instances.append(pending_time)
            else:
                break
        return time_instances

    def setupUE(self):
        UE_Transmission_Time  = self.setup_trasnmission_time(start_time=self.startTime, end_time=self.simEndTime, lambda_=self.transmission_rate)
        self.UE_TRANSMISSIONS.set_transmission_time(UE_Transmission_Time)


    def setup_trasnmission_time(self,start_time, end_time, lambda_):
        #return math_toolkit.random_generator(start_time, end_time, lambda_ )
        return math_toolkit.generate_transmission_times(lambda_, start_time,end_time)

    def pending_ULPacket(self, UL_DATA_PACKET_sequence_id, UL_DATA_PACKET_timeStampTransmission):
        appTransTime, appSeqID = self.UE_TRANSMISSIONS.pending_transmission()


    def check_for_transmission(self,current_time):
        # return math_toolkit.binary_search(self.transmission_time,current_time)
        if (not(self.check_transmission_queue()) and self.UE_TRANSMISSIONS.check_earliest_transmission() <= current_time):
            return True
        return False 
    
    def check_transmission_queue(self):
        if(len(self.UE_TRANSMISSIONS.transmission_time) == 0):
            return True #empty
        return False

    def transmission_succesful(self,ulPacketSequencID,APSector):
        transmission_time_intiated, UL_packet = self.UE_TRANSMISSIONS.transmit_success(ulPacketSequencID,APSector)
        return transmission_time_intiated,UL_packet

    def connect_to_AP(self, AP):
            self.AP = AP

    def UL_Transmit(self):
        distance = None
        if(self.LoS == 1):
            distance = math_toolkit.euclidean_distance(self.xCor,self.yCor,self.AP.x,self.AP.y)
        elif(self.NLOS == 1):
            index = self.bestNLOSLink
            distance = math_toolkit.euclidean_distance(self.xCor,self.yCor,self.reflect_x[index],self.reflect_y[index]) + math_toolkit.euclidean_distance(self.reflect_x[index],self.reflect_y[index],self.AP.x,self.AP.y) 
        else:
            print("ERROR: UL Transmit Intiated, but NO LOS or NLOS is available. ")
        return channel.link_budget(self.p_tx, distance, self.AP.maxBandwidth,self.txGain+self.AP.rxGain,self.AP.f_c_UL, 0)
    
    def reset_transmission(self):
        self.LoS = 0
        self.NLOS = 0

    def intitiate_transmission(self, mirrors,num_mirrors,time):
        p_rx = None
        data_rate = None
        BER = None
        mod_scheme = None
        if(self.mirror_setup == False):
            UE.mirrors_with_coverage(self, mirrors, num_mirrors)
            self.mirror_setup = True
        if(self.AP.get_currentSector(time) == self.mySector):
            #LOS Transmission
            self.LoS = 1
            self.NLOS = -1
            p_rx, data_rate, BER, mod_scheme = self.UL_Transmit()
        else:
            self.LoS  = 0
            self.NLOS = 0
            csector = self.AP.get_currentSector(time)
            signal_sector_index = math_toolkit.find_index(self.sector_mapping, csector)
            if(signal_sector_index== None):
                self.NLOS = 0
            else:
                self.NLOS = 1
                self.bestNLOSLink = signal_sector_index
                p_rx, data_rate, BER, mod_scheme = self.UL_Transmit()
        return p_rx, data_rate, BER, mod_scheme


            





    






















































































    # def setup_valid_reflection_vectors(self, AP, current_sector):
    #     self.reflect_x          = []
    #     self.reflect_y          = []
    #     self.reflect_slope      = []
    #     self.reflect_intercept  = []
    #     self.incident_slope     = []
    #     self.incident_intercept = []
    #     self.NLOS = 0

    #     x_l = self.xCor 
    #     y_l = self.yCor
    #     x_o = AP.x 
    #     y_o = AP.y
    #     mirror = self.my_mirrors
    #     for i in range(len(self.my_mirrors)):
    #         x1 = mirror[i].xCorP1
    #         y1 = mirror[i].yCorP1
    #         x2 = mirror[i].xCorP2
    #         y2 = mirror[i].yCorP2
    #         tilt_angle = math.radians(mirror[i].angleTilt)
    #         boundary_points = np.linspace(0, 1, 1000)
    #         reflect_x=0
    #         reflect_y=0
    #         reflect_slope=0
    #         reflect_intercept=0
    #         incident_slope=0
    #         incident_intercept=0
    #         self.NLOS = 0
    #         for s in boundary_points:
    #             # Compute the boundary point
    #             x_b = x1 + s * (x2 - x1)
    #             y_b = y1 + s * (y2 - y1)
                
    #             # Incident vector from light source to boundary point
    #             incident_vector = np.array([x_b - x_l, y_b - y_l])
    #             incident_vector = incident_vector / np.linalg.norm(incident_vector)  # Normalize
                
    #             incident_slope     = (y_b - y_l) /(x_b - x_l)
    #             incident_intercept = y_l - (incident_slope*x_l)
    #             # Mirror normal vector at the boundary point
    #             mirror_normal = np.array([-1 * np.sin(tilt_angle), np.cos(tilt_angle)])
                
    #             # Reflection using the law of reflection
    #             reflection_vector = incident_vector - 2 * np.dot(incident_vector, mirror_normal) * mirror_normal
    #             # print("Reflection Vector")
    #             # print(reflection_vector)
    #             # Compute the slope of the reflected ray
    #             if reflection_vector[0] != 0:  # Ensure no division by zero
    #                 slope = reflection_vector[1] / reflection_vector[0]
    #             else:
    #                 slope = np.inf  # Vertical line
                
    #             # Line equation of the reflected ray: y = slope * x + intercept
    #             intercept = y_b - slope * x_b
    #             # Check if the reflected ray intersects the observer
    #             print("Left Boundary: " + str(AP.sector_leftBoundary[int(current_sector-1)][2])+", Right Boundary: " + str(AP.sector_rightBoundary[int(current_sector-1)][2])
    #                   + "myPoint: " + str(abs(math.degrees(math.atan2(reflection_vector[1] ,reflection_vector[0])))) + ". Current Sector: " + str(current_sector)
    #                   )
                
    #             if slope != np.inf and (AP.sector_leftBoundary[int(current_sector-1)][2]<=abs(+math.degrees(math.atan2(reflection_vector[1] ,reflection_vector[0]))) <= AP.sector_rightBoundary[int(current_sector-1)][2]):
    #                 y_at_observer = slope * x_o + intercept
    #                 # print("Y at Observer: " + str(y_at_observer))
    #                 if np.isclose(y_at_observer, y_o, atol=1):
    #                     # print(f"Intersection found! Point on mirror: ({x_b:.2f}, {y_b:.2f})")
    #                     # print(x_b)
    #                     if(abs(y_at_observer) < reflect_intercept  ):
    #                             self.reflect_x.append(reflect_x)
    #                             self.reflect_y.append(reflect_y)
    #                             self.reflect_slope.append(reflect_slope)
    #                             self.reflect_intercept.append(reflect_intercept)
    #                             self.incident_slope.append(incident_slope)
    #                             self.incident_intercept.append(incident_intercept)
    #                             self.mirror_mapping.append(i)
    #                             self.NLOS = 1
    #                             print("ADDED ONE")
    #                             return      
    #             elif slope == np.inf and (AP.sector_leftBoundary[int(current_sector-1)][2]<=360-math.degrees(math.atan(slope)) <= AP.sector_rightBoundary[int(current_sector-1)][2]):
    #                 # Special case: vertical line, check if x_b matches x_o
    #                 if np.isclose(x_b, x_o, atol=1):
    #                     # print(f"Vertical ray intersects at ({x_b:.2f}, {y_b:.2f})")
    #                     UE[0].reflect_x = x_b
    #                     UE[0].reflect_y = y_b
    #                     UE[0].reflect_slope = slope
    #                     UE[0].reflect_intercept = intercept
    #                     UE[0].NLOS = 1
    #                     return
    #             else:
    #                 continue
    

    # def setup_all_reflection_vectors(self, AP):
    #     x_l = self.xCor 
    #     y_l = self.yCor
    #     x_o = AP.x 
    #     y_o = AP.y
    #     mirror = self.my_mirrors
    #     for i in range(len(self.my_mirrors)):
    #         x1 = mirror[i].xCorP1
    #         y1 = mirror[i].yCorP1
    #         x2 = mirror[i].xCorP2
    #         y2 = mirror[i].yCorP2
    #         tilt_angle = math.radians(mirror[i].angleTilt)
    #         boundary_points = np.linspace(0, 1, 1000)
    #         reflect_x=0
    #         reflect_y=0
    #         reflect_slope=0
    #         reflect_intercept=0
    #         incident_slope=0
    #         incident_intercept=0
    #         self.NLOS = 0

    #         for s in boundary_points:
    #             # Compute the boundary point
    #             x_b = x1 + s * (x2 - x1)
    #             y_b = y1 + s * (y2 - y1)
                
    #             # Incident vector from light source to boundary point
    #             incident_vector = np.array([x_b - x_l, y_b - y_l])
    #             incident_vector = incident_vector / np.linalg.norm(incident_vector)  # Normalize
                
    #             incident_slope     = (y_b - y_l) /(x_b - x_l)
    #             incident_intercept = y_l - (incident_slope*x_l)
    #             # Mirror normal vector at the boundary point
    #             mirror_normal = np.array([-1 * np.sin(tilt_angle), np.cos(tilt_angle)])
                
    #             # Reflection using the law of reflection
    #             reflection_vector = incident_vector - 2 * np.dot(incident_vector, mirror_normal) * mirror_normal
  
    #             if reflection_vector[0] != 0:  # Ensure no division by zero
    #                 slope = reflection_vector[1] / reflection_vector[0]
    #             else:
    #                 slope = np.inf  # Vertical line
                
    #             # Line equation of the reflected ray: y = slope * x + intercept
    #             intercept = y_b - slope * x_b
    #             # Check if the reflected ray intersects the observer
     
    #             if slope != np.inf:
    #                 y_at_observer = slope * x_o + intercept
    #                 if np.isclose(y_at_observer, y_o, atol=1):
    #                     if(self.NLOS<=0 or abs(y_at_observer) < abs(reflect_intercept)  ):
    #                         reflect_x=x_b
    #                         reflect_y=y_b
    #                         reflect_slope=slope
    #                         reflect_intercept=intercept
    #                         incident_slope=incident_slope
    #                         incident_intercept=incident_intercept
    #                         self.NLOS = 1
    #                         #elseif is wrong, it takes the next point. fix later
    #                     elif(abs(y_at_observer) >= abs(reflect_intercept) and self.NLOS==1):
    #                             self.reflect_x.append(reflect_x)
    #                             self.reflect_y.append(reflect_y)
    #                             self.reflect_slope.append(reflect_slope)
    #                             self.reflect_intercept.append(reflect_intercept)
    #                             self.incident_slope.append(incident_slope)
    #                             self.incident_intercept.append(incident_intercept)
    #                             self.mirror_mapping.append(i)
    #                             self.sector_mapping.append(AP.return_mySector(x_b,y_b))
    #                             break      
    #             elif slope == np.inf :
    #                 # Special case: vertical line, check if x_b matches x_o
    #                 if np.isclose(x_b, x_o, atol=1):
    #                     print("ERROr -slope - inf")
    #                     exit
    #                     # print(f"Vertical ray intersects at ({x_b:.2f}, {y_b:.2f})")
    #                     UE[0].reflect_x = x_b
    #                     UE[0].reflect_y = y_b
    #                     UE[0].reflect_slope = slope
    #                     UE[0].reflect_intercept = intercept
    #                     UE[0].NLOS = 1
    #                     return
    #             else:
    #                 continue
                    



