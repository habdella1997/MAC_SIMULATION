import sys
from MAC import mac_ap, mac_ue
import math
import channel
import Objects.AP as AP
import Objects.UE as UE
# import Objects.room as ROOM
from room2 import room2
from typing import List
import math_toolkit
from Objects.transmission2 import *
from Logging.transmission_logging import Logger
import RF
import utilities
import numpy as np
from collections import deque

#packet sizes in bytes.

class MAC_Controller:
    # Misc Control Params
    AP_STARTING_SECTOR        = 1     # Sector in which AP begin upon start of simulation 
    BOUNDARY_OF_ROOM          = 0.2   # Used to limit the loaction of UE handset to not be very close or on the room edge 
    UE_MAX_RETRANSMISSION     = 10  # Limits the number of Transmissions
    SectorTransitionTimeDelay =  0#1*(10**-9)  #2 *(10**-6) # [nS] time to move from one sector to another 

    #Packet Params
    CONTROL_PACKET_SIZE  = 200 #bytes
    CONTROL_PACKET_BEFF  = 2 #bandwidth effeciency for QPSK
    PAYLOAD_PACKET_SIZE  = 64000 #bytes
    
    #15/16 Encoding Scheme
    FEC_NUMERATOR   = 15 
    FEC_DENOMINATOR = 16

    # Control Togales
    Processing_Delay_Accounted = False
    MAX_DISTANCE_CONTROL_SUPPORT = - 1
    
    # MAC Protocol: ADAPT, ADAPT2, etc.
    # sectorTime: time AP Spends in each sector depends on the MAC Protocol [S]
    # room: The Simulation Room
    # uePower: Transmission Power of UE [watts]
    # apPower: Tranmission Power  of AP [watts]
    def __init__(self, mac_protocol, systemBandwidth, room:room2):
        self.mac_protocol        = mac_protocol
        self.sectorTime          = 0
        self.simRoom             = room
        self.bandwidth           = systemBandwidth
        self.AP                  = []
        self.UE_List             = []

        # Used to Compute New Packet Sizes based on Coding Scheme Utilized. <- Defined in packetEncoding()
        self.controlPacketLength_Encoded           = 0
        self.controlPacketTransmissionRate_Encoded = 0
        self.dataPacketLength_Encoded              = 0
        self.ue_coordinates = None
    
    def return_ue_coordinates(self):
        return self.ue_coordinates

    # TOP LEVEL Function for seting up the MAC
    # NumAP : Number of AP units: Currently only supporting one AP per simulation
    # numUE : Number of UE units
    # beamwidth : beamdWidth in degrees -> used to compute the antenna gain, and number of sectors. 
    # UE_Power: UE Transmit Power in watts 
    # AP_Power: AP Transmit Power in watts
    # frequency: Center Frequency 
    # UE_uplinkTransmissionRate: The transmission rate of UE. Used to compute the transmission time. A higher value means the UE will be more likely to transmit a packet.  
    def setupMAC(self,numAP, lambda_density, beamWidth, UE_Power, AP_Power,frequency, UE_uplinkTransmissionRate,startTime,simEndTime,logger:Logger,ue_coordinates,mirrors):
        self.setup_devices(numAP, lambda_density, beamWidth, UE_Power, AP_Power,frequency, UE_uplinkTransmissionRate,startTime,simEndTime,ue_coordinates)
        self.simRoom.setup_mirrors_in_room(mirrors)
        self.simRoom.setup_fov_generic(mirrors, len(mirrors), self.AP)
        self.los_linkbudget()
        self.packetEncoding()
        RESULTS_LATENCY   = None
        RESULTS_DATA_RATE = None
        RESULTS_UE_ID     = None 
        NLoSReflections         = None
        if(self.mac_protocol == "ADAPT"):
            RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID = self.macAdapt(logger,simEndTime)
        else:
            RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID,NLoSReflections = self.macHussam(logger,simEndTime)
        return RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID,NLoSReflections

    def collision_detection_ul(self,packets):
        packets_dropped = []
        packets_success = []

        for packet in packets:
            success = True
            arrival_time  = packet.timeStampArrival
            transmit_time = packet.timeStampTransmission
            for next_packet in packets:
                if (next_packet == packet):
                    continue
                if(transmit_time < next_packet.timeStampTransmission):
                    if(arrival_time <= next_packet.timeStampTransmission):
                        continue # no collision here
                elif(transmit_time > next_packet.timeStampTransmission):
                    if(transmit_time >= next_packet.timeStampArrival):
                        continue
                else: 
                    pass
                success = False
                break
            if(success):
                packets_success.append(packet)
            else:
                packets_dropped.append(packet)
        return packets_dropped,packets_success
    
    
 
    def collision_detection_ul2(self,packets,MESSAGES_Logging):
        if(len(packets) == 1):
            return [],packets
        packets_dropped = []
        packets_success = []

        for packet in packets:
            success = True
            arrival_time  = packet.timeStampTransmission + packet.propagationDelay
            occupied_time = arrival_time + packet.transmissionDelay #time in which RX is receiving data
            sender = packet.sender
            sender_next_packet = None
            for next_packet in packets:
                if (next_packet == packet):
                    continue
                arrival_time_next_packet  = next_packet.timeStampTransmission + packet.propagationDelay
                occupied_time_next_packet = arrival_time_next_packet + packet.transmissionDelay
                sender_next_packet = next_packet.sender
                if(arrival_time < arrival_time_next_packet):
                    if(occupied_time <= arrival_time_next_packet):
                        continue # no collision here
                elif(arrival_time > arrival_time_next_packet):
                    if(arrival_time >= occupied_time_next_packet):
                        continue
                else: 
                    pass
                success = False
                break
            if(success):
                packets_success.append(packet)
                MESSAGES_Logging.append("Packet " + packet.packetType + "with seq id: " + str(packet.sequence_id)+ " occured no collision")
                MESSAGES_Logging.append("UE device: " + str(packet.sender) + " sent Packet w/ no collision")
            else:
                if(sender == sender_next_packet):
                    print("UE colliding w/ itself bug present")
                    sys.exit(1)
                packets_dropped.append(packet)
                MESSAGES_Logging.append("Packet " + packet.packetType +"  with seq id: " + str(packet.sequence_id) +", "+ str(next_packet.sequence_id) +"has been dropped due to collision")
                MESSAGES_Logging.append("UE device: " + str(packet.sender) + ", and UE Device: " + str(next_packet.sender) + " sent Packets that collided with one another")
                MESSAGES_Logging.append("First Packet Transmission and Arrival Times are: " + str(packet.timeStampTransmission) + ", " +str(packet.timeStampArrival))
                MESSAGES_Logging.append("First Packet Transmission and Arrival Times are: " + str(next_packet.timeStampTransmission) + ", " +str(next_packet.timeStampArrival))
        return packets_dropped,packets_success
        

    def setup_devices(self, numAP, lambda_density, beamWidth, UE_Power, AP_Power,frequency, UE_uplinkTransmissionRate,startTime,simEndTime,fixed_ue_coordinates):
        #Top Function to Setup the UE Device handset and AP
        AP_RFBox, UE_RFBox = self.setup_RFEquipment(beamWidth, UE_Power, AP_Power, frequency) # get the gain of the system. 
        if(fixed_ue_coordinates == None):
            ue_coordinates = None
        else:
            ue_coordinates = fixed_ue_coordinates
        #setup AP Device
        if (numAP > 1 ):
            print("Multi-AP is not currently supported")
            sys.exit(1)
        else:
            APDevice = AP.AP(AP_RFBox, MAC_Controller.AP_STARTING_SECTOR)
            APDevice.setupAP()
            self.AP = APDevice
            area = math.pi * ((self.simRoom.length - (MAC_Controller.BOUNDARY_OF_ROOM*self.simRoom.length))  **2)
            expected_nodes = int(np.random.poisson(lambda_density * area))
            if(ue_coordinates == None):
                ue_coordinates = math_toolkit.randomCoordinates(expected_nodes, (((self.simRoom.length - (MAC_Controller.BOUNDARY_OF_ROOM*self.simRoom.length))) ))
            self.ue_coordinates = ue_coordinates
            print("Number of Devices: " + str(len(ue_coordinates)))
        #Setup UE Devices: 
        for i, (x, y) in enumerate(ue_coordinates, 1):
            UE_DEVICE = UE.UE(x,y,MAC_Controller.UE_MAX_RETRANSMISSION,UE_RFBox,UE_uplinkTransmissionRate,startTime,simEndTime)
            UE_DEVICE.setupUE()
            UE_DEVICE.connect_to_AP(self.AP)
            self.UE_List.append(UE_DEVICE)
        # for i in range(numUE):
        #     boundaryx = self.simRoom.length - MAC_Controller.BOUNDARY_OF_ROOM*self.simRoom.length
        #     boundaryy = self.simRoom.width  - MAC_Controller.BOUNDARY_OF_ROOM*self.simRoom.width
        #     xCor, yCor = math_toolkit.random_XY_coordinates(boundaryx,boundaryy)
        #     UE_DEVICE = UE.UE(xCor,yCor,MAC_Controller.UE_MAX_RETRANSMISSION,UE_RFBox,UE_uplinkTransmissionRate,simEndTime)
        #     UE_DEVICE.setupUE()
        #     UE_DEVICE.connect_to_AP(self.AP)
        #     self.UE_List.append(UE_DEVICE)


    
    def setup_RFEquipment(self, beamWidth, UE_Power, AP_Power, frequency):
        self.UE_Power  = UE_Power
        self.AP_Power  = AP_Power
        gain = RF.define_gain(beamWidth)
        AP_RFBox = RF.RFBox(gain,AP_Power,frequency,beamWidth,self.bandwidth)
        UE_RFBox = RF.RFBox(gain,UE_Power,frequency,beamWidth,self.bandwidth)
        return AP_RFBox, UE_RFBox

    def los_linkbudget(self):
        #Assuming A square room
        d_support = channel.max_distance(self.AP.RFBox.power , self.bandwidth, self.AP.RFBox.gain, self.AP.RFBox.frequency)
        MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT = self.simRoom.width
        if(d_support < self.simRoom.width):
            print("Failure -> Room Distance is greater than channel support")
            sys.exit(1)
        else: 
            pass

    def packetEncoding(self):
        control_packet_length    = MAC_Controller.CONTROL_PACKET_SIZE * 8 #convert to bits
        data_packet_length       = MAC_Controller.PAYLOAD_PACKET_SIZE * 8
        
        control_length_encoded   = math.ceil(control_packet_length / MAC_Controller.FEC_NUMERATOR) * MAC_Controller.FEC_DENOMINATOR
        payload_length_encoded   = data_packet_length #math.ceil(data_packet_length / MAC_Controller.FEC_NUMERATOR) * MAC_Controller.FEC_DENOMINATOR
    
        control_transmission_rate =  self.bandwidth * self.CONTROL_PACKET_BEFF
        
        self.controlPacketLength_Encoded           = control_length_encoded
        self.controlPacketTransmissionRate_Encoded = control_transmission_rate
        self.dataPacketLength_Encoded              = payload_length_encoded
    
    def return_devices(self):
        return self.AP, self.UE_List    
    def processingTimeDelay(self):
        pass
        # #Processing Time Delay Setup
        # BASEBAND_CLOCKING = 128e6
        # PERCENTAGE_OF_TIME_DELAY = 0.2
        # if(self.Processing_Delay_Accounted):
        #     PROCESSING_TIME_PACKET_control = newPacket_length * (1/BASEBAND_CLOCKING) * PERCENTAGE_OF_TIME_DELAY
        # else:
        #     PROCESSING_TIME_PACKET_control = 0

    def generateTimeSlots(self, startTime, endTime, payloadLength, transmissionRate, distance):
        propDelay = channel.compute_propagationDelay(distance)
        minTransmitDelay = channel.compute_transmissionTime(payloadLength,transmissionRate)
        timeSlotDuration = minTransmitDelay + propDelay
        timeSlots = []
        currentTime = startTime
        while currentTime < endTime:
            timeSlots.append(currentTime)
            currentTime += timeSlotDuration
            if(currentTime>=endTime):
                break
        return timeSlots


    def checkTimeWasted(self, timeSlots, sectorTime):
        pass



    def macAdapt(self, logger:Logger, endTime):
        print("ADAPT Simulation Start")
        print("Simulation End Time: " + str(endTime))
        sectorTimeElapsed = 0
        apSector = 1 # need to define Sector from here since its Dynamic
        cycle_period = []
        #ADAPT PARAMETERS:
        RANDOM_BACK_OFF_TIME_MAX = 10 *(10**-9) #[nS]
        PAYLOAD_SIZE_BITS  = MAC_Controller.PAYLOAD_PACKET_SIZE * 8
        
        MAC_UEDEVICES = []
        mac_ue.macUE.RANDOM_BACKOFF_MAXTIME =  RANDOM_BACK_OFF_TIME_MAX
        mac_ue.macUE.RANDOM_BACKOFF_MINTIME = 0
        
        #create MAC_UE objects for each UE
        for ue_device in self.UE_List:
            MAC_UEDEVICES.append(mac_ue.macUE(ue_device))

        
        #Simulation LOOP Variables
        simulationTotalTimeElapsed = 0
        MACAP = mac_ap.macAP(self.AP,apSector)
        time_scale = 1

        Packet.CONTROL_PACKET_LENGTH = self.controlPacketLength_Encoded 
        Packet.CONTROL_PACKET_RATE   = self.controlPacketTransmissionRate_Encoded
        Packet.DATA_PACKET_LENGTH    = self.dataPacketLength_Encoded
        
        #Results:
        RESULT_LATENCY   = []
        RESULT_DATA_RATE = []
        RESULT_UE_ID     = []

        PROCESSING_TIME_PACKET_control = 0

        RTS_Failures = 0
        Total_RTS    = 0
        utilities.status = 0  
        #each iteration is a new sector -> defined to suit the ADAPT MODEL 
        while True:
            utilities.print_status(simulationTotalTimeElapsed,endTime)
            PACKETS_Logging = []
            #new Sector: Send CTA
            max_time_elapsed_CTA = MACAP.maxControlDelay(Packet.CONTROL_PACKET_LENGTH, MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT, Packet.CONTROL_PACKET_RATE ,PROCESSING_TIME_PACKET_control) / time_scale
            max_time_elapsed_RTS = max_time_elapsed_CTA
            total_wait_time = simulationTotalTimeElapsed + max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX
            
            # ASK AP to create the CTA Packet and time-stamp it
            CTA_PACKET = MACAP.create_CTA_Packet(simulationTotalTimeElapsed,apSector)
            MACUE_devices_withTransmission_Request = []
            
            devices_done = 0
            for device in MAC_UEDEVICES: #check_Transmission_Capbaility(self,time_window_right,apSector, linkType):
                if(device.return_UE_Sector() == MACAP.currentSector):
                    CTA_PACKET.addRecepients(device.ue_device.id)
                if(device.check_Transmission_Capbaility(total_wait_time,MACAP.currentSector,"LoS")):
                    MACUE_devices_withTransmission_Request.append(device)
                if(device.check_done_transmissions()):
                    devices_done += 1
            
            if(devices_done == len(MAC_UEDEVICES)-1):
                break
            RTS_PACKETS = []
 
            #check which of the UE_devices_withTransmission_Request can be serviced-> 1.RTS needs to arrive before total_wait_time, 2. AP and UE need to be in the same sector
            for MACUE_device in MACUE_devices_withTransmission_Request:
                MACUE_device.process_CTA_packet(CTA_PACKET)
                RTS_PACKET = MACUE_device.create_RTS_Packet("LoS",MACUE_device.ue_device.UE_TRANSMISSIONS.check_earliest_transmission()) 
                if(RTS_PACKET.timeStampArrival < total_wait_time): #UE was able to send an RTS before elapsed wait time. After elapsed wait time, AP turns into new sector. 
                    #Make sure link can be closed otherwise AP wont recieve it ...
                    if (MACUE_device.distanceToAP <= self.MAX_DISTANCE_CONTROL_SUPPORT): #note that i am using the control support here
                        RTS_PACKETS.append(RTS_PACKET)
                    else:
                        #failed Transmission due to link budget
                        # Log A link failure due to LINK NOT CLOSING
                        pass

                else:
                    #failed due to time, missed my opportunity, wait for next cyle
                    #LOG TIMING FAILURE
                    pass
            
            RTS_DROPPED,RTS_SUCCESS = self.collision_detection_ul2(RTS_PACKETS)
            RTS_Failures += len(RTS_DROPPED)
            Total_RTS += len(RTS_PACKETS)

            for dropped_packet in RTS_DROPPED:
                for device in MACUE_devices_withTransmission_Request:
                    if dropped_packet.sender == device.ue_device.id:
                        device.process_RTS_collision()

            

            # if(len(RTS_DROPPED) > 0):
            #     print("ERROR Collision Not Expected")
            #     import collision_detection_tester
            #     collision_detection_tester.plot_packets(RTS_PACKETS,RTS_DROPPED,RTS_SUCCESS, RTS_PACKETS[0].timeStampTransmission + 0.005, 20)
            #     print(len(RTS_PACKETS))
            #     sys.exit(1)
            RTS_PACKETS = RTS_SUCCESS


            if(len(RTS_PACKETS)==0): #No Transmission Needed in this in time slot
                simulationTotalTimeElapsed += (max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay)
                apSector += 1
                if(apSector > self.AP.number_of_sectors):
                    cycle_period.append(max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay)
                    apSector = 1 
                MACAP.currentSector = apSector
                logger.log_packet(CTA_PACKET)
                if simulationTotalTimeElapsed > endTime:
                    break
                continue



            CTS_PACKET = MACAP.create_CTS_Packet(RTS_PACKETS,MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT,total_wait_time)

            UL_PACKETS  = []
            for MACUE_device in MACUE_devices_withTransmission_Request:
                MACUE_device.process_CTS_packet(CTS_PACKET)
                UL_PACKET = MACUE_device.create_ULDATA_Packet()
                if(UL_PACKET != None):
                    UL_PACKETS.append(UL_PACKET)
            

            
            UL_DROPPED, UL_SUCCESS  = self.collision_detection_ul(UL_PACKETS)
            collision_processed = 0

            if(len(UL_DROPPED) > 0):
                import collision_detection_tester
                collision_detection_tester.plot_packets(UL_PACKETS,UL_DROPPED,UL_SUCCESS, UL_PACKETS[0].timeStampTransmission + 0.005, 20)
                print(len(UL_PACKETS))
                sys.exit(1)
                

                    

            ACK_PACKETS = MACAP.create_ACK_Packet(UL_PACKETS,MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT)

            for MACUE_device in MACUE_devices_withTransmission_Request:
                latency, data_rate = MACUE_device.process_ACK_packet(ACK_PACKETS)
                if latency != None and data_rate != None:
                    RESULT_LATENCY.append(latency)
                    RESULT_DATA_RATE.append(data_rate)
                    RESULT_UE_ID.append(MACUE_device.ue_device.id)
            
            PACKETS_Logging.append(CTA_PACKET)
            PACKETS_Logging += RTS_PACKETS
            PACKETS_Logging.append(CTS_PACKET)
            PACKETS_Logging += UL_PACKETS
            PACKETS_Logging.append(ACK_PACKETS)
            
            for packet in PACKETS_Logging:
                if(packet == None):
                    continue
                logger.log_packet(packet)

            simulationTotalTimeElapsed += ((ACK_PACKETS.timeStampTransmission-simulationTotalTimeElapsed) + MAC_Controller.SectorTransitionTimeDelay)
            apSector += 1
            if(apSector > self.AP.number_of_sectors):
                apSector = 0 
                cycle_period.append(((ACK_PACKETS.timeStampTransmission-simulationTotalTimeElapsed) + MAC_Controller.SectorTransitionTimeDelay))
            MACAP.currentSector = apSector
            if simulationTotalTimeElapsed > endTime:
                break
        
        print("RTS Rate Of Failure: " + str(RTS_Failures / Total_RTS))
        print("\n\n Mean Cycle Period \n\n " +str(np.mean(cycle_period) * self.AP.number_of_sectors) + "Sec")
        return RESULT_LATENCY, RESULT_DATA_RATE, RESULT_UE_ID

    def macHussam(self, logger:Logger, endTime):
        print("Hussam Simulation Start")
        print("Simulation End Time: " + str(endTime))
        LoS_Sector_Time         = 10 * (10**(-6)) #Time Spent Per Sector Dedicated only for LoS Signaling
        LoS_RTS_Time_Percentage = 0.1 
        nLos_Sector_Time  = 10 * (10**(-6)) #2 * (10**(-6)) #Time Spent Per Sector Dedicated only for nLoS Signaling
        total_sector_Time = LoS_Sector_Time + nLos_Sector_Time 

        apSector = 1 # need to define Sector from here since its Dynamic
        
        # PARAMETERS:
        RANDOM_BACK_OFF_TIME_MAX = 10 *(10**-9) #[nS]
        
        MAC_UEDEVICES = []
        mac_ue.macUE.RANDOM_BACKOFF_MAXTIME =  RANDOM_BACK_OFF_TIME_MAX
        mac_ue.macUE.RANDOM_BACKOFF_MINTIME = 0
        
        #create MAC_UE objects for each UE
        for ue_device in self.UE_List:
            MAC_UEDEVICES.append(mac_ue.macUE(ue_device))

        
        #Simulation LOOP Variables
        simulationTotalTimeElapsed = 0
        MACAP = mac_ap.macAP(self.AP,apSector)
        time_scale = 1

        Packet.CONTROL_PACKET_LENGTH = self.controlPacketLength_Encoded 
        Packet.CONTROL_PACKET_RATE   = self.controlPacketTransmissionRate_Encoded
        Packet.DATA_PACKET_LENGTH    = self.dataPacketLength_Encoded
        
        #Results:
        RESULT_LATENCY   = []
        RESULT_DATA_RATE = []
        RESULT_UE_ID     = []

        PROCESSING_TIME_PACKET_control = 0

        RTS_Failures = 0
        Total_RTS    = 0

        NLoS_UL_failures = 0
        NLOS_Total_UL_Packets = 0
        utilities.status = 0  
        #each iteration is a new sector -> defined to suit the ADAPT MODEL 

        UE_ID_in_Simulation = [x.ue_device.id for x in MAC_UEDEVICES]
        NLoS_Path_Mapping   = dict((key,[[],[]]) for key in UE_ID_in_Simulation)

        while True:
            utilities.print_status(simulationTotalTimeElapsed,endTime)
            PACKETS_Logging = []
            MESSAGES_Logging = [] 
            #new Sector: Send CTA
            sector_start_time = simulationTotalTimeElapsed
            sector_end_time   = sector_start_time + total_sector_Time #Time spent in this sector
            MESSAGES_Logging.append("The start time of this sector is : " + str(sector_start_time))
            # ASK AP to create the CTA Packet and time-stamp it
            CTA_PACKET = MACAP.create_CTA_Packet(simulationTotalTimeElapsed,apSector)
            MACUE_devices_withTransmission_Request = []
            RTS_PACKETS = []
            devices_done = 0
            MESSAGES_Logging.append("RTS END TIME is set to : " + str(sector_start_time + (LoS_Sector_Time*LoS_RTS_Time_Percentage)))
            for device in MAC_UEDEVICES: #check_Transmission_Capbaility(self,time_window_right,apSector, linkType):
                if(device.return_UE_Sector() == MACAP.currentSector):
                    CTA_PACKET.addRecepients(device.ue_device.id)
                    device.process_CTA_packet(CTA_PACKET)
                    MESSAGES_Logging.append("UE ID: " + str(device.ue_device.id))
                    MESSAGES_Logging.append("CTA PACKED Arrived at time instant: " + str(device.lastCTA_ArrivalTime))
                    UE_RTS_ENDTIME = device.OmniMAC_RTSTransmissionTime(LoS_Sector_Time*LoS_RTS_Time_Percentage,0.2)
                    MESSAGES_Logging.append("UE RTS end time computed to be: " + str(UE_RTS_ENDTIME))
                    if(device.check_Transmission_Capbaility(sector_start_time+UE_RTS_ENDTIME,MACAP.currentSector,"LoS")):
                        MESSAGES_Logging.append("UE has something to transmit")
                        MACUE_devices_withTransmission_Request.append(device)
                        UL_Valid_Transmissions = device.ue_device.check_number_packets(sector_start_time+UE_RTS_ENDTIME)
                        MESSAGES_Logging.append("Packet Time slots that pass the time criteria: "+ str(' '.join(map(str, UL_Valid_Transmissions))))
                        RTS_PACKET = device.create_RTS_Packet("LoS",sector_start_time+UE_RTS_ENDTIME,UL_Valid_Transmissions)
                        MESSAGES_Logging.append("RTS PACKET created with seq id: " + str(RTS_PACKET.sequence_id)) 
                        RTS_PACKETS.append(RTS_PACKET)
                    else:
                        MESSAGES_Logging.append("UE has nothing to transmit")
                        
                if(device.check_done_transmissions()):
                    devices_done += 1

            if(devices_done == len(MAC_UEDEVICES)):
                break

            ## Now we have all the RTS PACKETS. Lets drop the ones with collosions 
            RTS_DROPPED,RTS_SUCCESS = self.collision_detection_ul2(RTS_PACKETS,MESSAGES_Logging)
            MESSAGES_Logging.append("Total RTS Packets: " + str(len(RTS_PACKETS)) + ", Dropped RTS packets: " + str(RTS_DROPPED))
            RTS_Failures += len(RTS_DROPPED)
            Total_RTS += len(RTS_PACKETS)
            already_processed_ue = []
            for dropped_packet in RTS_DROPPED:
                for device in MACUE_devices_withTransmission_Request:
                    if dropped_packet.sender == device.ue_device.id and (not(dropped_packet.sender in already_processed_ue)):
                        device.process_RTS_collision()
                        already_processed_ue.append(dropped_packet.sender)
            
            RTS_PACKETS = RTS_SUCCESS
            #print("RTS DROPPED: " + str(len(RTS_DROPPED)))


            # if(len(RTS_PACKETS)==0): #No Transmission Needed in this in time slot
            #     MESSAGES_Logging.append("No RTS packets has been sent.")
            #     simulationTotalTimeElapsed += LoS_Sector_Time + nLos_Sector_Time
            #     apSector += 1
            #     if(apSector > self.AP.number_of_sectors):
            #         apSector = 1 
            #     MACAP.currentSector = apSector
            #     logger.log_packet(CTA_PACKET)
            #     logger.log_action(MESSAGES_Logging)
            #     if simulationTotalTimeElapsed > endTime:
            #         break
            #     continue
                
            CTS_PACKET = None
            if(len(RTS_PACKETS)>0):
                # Now we have a list of RTS that will arrive at AP succesfully. Lets have the AP process them and send out the CTS with the UL grants. 
                CTS_PACKET = MACAP.create_CTS_Packet(RTS_PACKETS,MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT,sector_start_time+(LoS_Sector_Time*LoS_RTS_Time_Percentage),sector_start_time+ LoS_Sector_Time)
                MESSAGES_Logging.append("The UL Start Time is set to be: " + str(sector_start_time+(LoS_Sector_Time*LoS_RTS_Time_Percentage)))
                MESSAGES_Logging.append("The UL End Time is set to be: " + str(sector_start_time+ LoS_Sector_Time))
                for indexer,grantsApproved in enumerate(CTS_PACKET.allocatedTimeSlots):
                    timeSlot = CTS_PACKET.allocatedTimeSlots[indexer]
                    ueID     = CTS_PACKET.allocatedUEID[indexer]
                    MESSAGES_Logging.append("UE : " + str(ueID) + ", has been alloacted the following time slot: " + str(timeSlot))


            UL_PACKETS  = []
            if(CTS_PACKET != None):
                for ue_ID in CTS_PACKET.allocatedUEID:
                    for device in MACUE_devices_withTransmission_Request:
                        if device.ue_device.id == ue_ID:
                            device.process_CTS_packet(CTS_PACKET)
                            UL_PACKET = device.create_ULDATA_Packet()
                            UL_PACKETS.append(UL_PACKET)
                            MESSAGES_Logging.append("UEID: " + str(ue_ID) + "generated the following ul packet: " + str(UL_PACKET.sequence_id))
                
            ACK_Packets = []
            if(len(UL_PACKETS) >0):
            #print("Num UL Packets: " + str(len(UL_PACKETS)))
                UL_DROPPED, UL_SUCCESS = self.collision_detection_ul2(UL_PACKETS,MESSAGES_Logging)

                for droppedLoSPacket in UL_DROPPED:
                    for MACUE_device in MACUE_devices_withTransmission_Request_NLoS:
                        if droppedLoSPacket.sender == MACUE_device.ue_device.id:
                            MACUE_device.processULDataFailure(droppedLoSPacket, "LoS")
                UL_PACKETS = UL_SUCCESS

                
                for UL_Packet in UL_PACKETS:
                    ACK_Packet = MACAP.create_ACK_PacketNLoS(UL_Packet)
                    ACK_Packets.append(ACK_Packet)

            
            for MACUE_device in MACUE_devices_withTransmission_Request:
                for ACK_Packet in ACK_Packets:
                    if(MACUE_device.ue_device.id == ACK_Packet.ueIDlist[0]):
                        MESSAGES_Logging.append("UEID : "+str(MACUE_device.ue_device.id) + "has receieved an ACK")
                        latency, data_rate = MACUE_device.process_ACK_packet_NLoS(ACK_Packet,"LoS",MACAP.currentSector)
                        if latency != None and data_rate != None:
                            RESULT_LATENCY.append(latency)
                            RESULT_DATA_RATE.append(data_rate)
                            RESULT_UE_ID.append(MACUE_device.ue_device.id)


            NLoS_RTS_Packets = []
            NLoS_UL_Packets = []
            MACUE_devices_withTransmission_Request_NLoS = []
            ## NLoS Links Start here:
            for device in MAC_UEDEVICES: #check_Transmission_Capbaility(self,time_window_right,apSector, linkType):
                nLoS_start_time = sector_start_time + LoS_Sector_Time
                nLoS_end_time   = nLoS_start_time + nLos_Sector_Time
                if(device.check_Transmission_Capbaility(nLoS_end_time,MACAP.currentSector,"nLoS")):
                    NLoS_start_endtime = math_toolkit.random_uniform_between(0,nLos_Sector_Time)
                    NLoS_device_endtime = math_toolkit.random_uniform_between(nLoS_start_time,nLoS_end_time)
                    UL_Valid_Transmissions = device.ue_device.check_number_packets(NLoS_device_endtime)
                    #create_ULDATA_Packet_NLoS(self,TransmissionTime,NLoS_DataRate,NLoS_Distance):
                    NLoS_Signal_highest,max_data_rate_highest,distance = device.setupNLoSLinks(MACAP.AP,MACAP.currentSector,self.simRoom)
                    
                    if(NLoS_Signal_highest == None or len(UL_Valid_Transmissions)==0 or NLoS_Signal_highest.NLoS==0):
                        continue
                    # else:
                    #     print("NLoS Aadded for ueid: " + str(device.ue_device.id))
                    

                    MACUE_devices_withTransmission_Request_NLoS.append(device)
                    UL_Packet = None
                    UL_Packet_Transmission_Time = -1
                    time_delta                  = math_toolkit.random_uniform_between(0,4e-6)
                    counter = 0 
                    for index,UL_Valid_Transmission in enumerate(UL_Valid_Transmissions):
                        if(counter == 1):
                            break
                        if(UL_Valid_Transmission < NLoS_device_endtime):

                            if(UL_Valid_Transmission > nLoS_start_time):
                                # UL_Packet = device.create_ULDATA_Packet_NLoS(UL_Valid_Transmission,max_data_rate_highest,distance)
                                UL_Packet_Transmission_Time = UL_Valid_Transmission + time_delta
                            else:
                                UL_Packet_Transmission_Time = nLoS_start_time  + time_delta
                            if(UL_Packet_Transmission_Time < nLoS_end_time):
                                UL_Packet = device.create_ULDATA_Packet_NLoS(UL_Packet_Transmission_Time,max_data_rate_highest,distance)
                                time_delta += UL_Packet.transmissionDelay + UL_Packet.propagationDelay + math_toolkit.random_uniform_between(0,4e-6)
                                NLoS_UL_Packets.append(UL_Packet)
                                NLoS_Path_Mapping[device.ue_device.id][0].append(UL_Packet.timeStampTransmission)
                                NLoS_Path_Mapping[device.ue_device.id][1].append(NLoS_Signal_highest)
                                counter +=1
                                if NLoS_Signal_highest.reflect_slope == 0:
                                    print("zero. ")
                            else:
                                break
                        
            

            UL_NLoS_DROPPED, UL_NLoS_SUCCESS = self.collision_detection_ul2(NLoS_UL_Packets,MESSAGES_Logging)

            NLoS_UL_failures += len(UL_NLoS_DROPPED)
            NLOS_Total_UL_Packets += len(NLoS_UL_Packets)

            for droppedNLoSPacket in UL_NLoS_DROPPED:
                for MACUE_device in MACUE_devices_withTransmission_Request_NLoS:
                    if droppedNLoSPacket.sender == MACUE_device.ue_device.id:
                        MACUE_device.process_UL_PacketFailure(droppedNLoSPacket, "NLoS",MACAP.currentSector)

            NLoS_UL_Packets = UL_NLoS_SUCCESS
            if(NLoS_UL_Packets):
                ACK_PACKETS_NLoS = []

                for NLoS_UL_Packet in NLoS_UL_Packets:
                    ACK_Packet = MACAP.create_ACK_PacketNLoS(NLoS_UL_Packet)
                    ACK_PACKETS_NLoS.append(ACK_Packet)


                for MACUE_device in MACUE_devices_withTransmission_Request_NLoS:
                    for ACK_PACKET_NLoS in ACK_PACKETS_NLoS:
                        if(MACUE_device.ue_device.id == ACK_PACKET_NLoS.ueIDlist[0]):
                            MESSAGES_Logging.append("UEID : "+str(MACUE_device.ue_device.id) + "has receieved an ACK")
                            latency, data_rate = MACUE_device.process_ACK_packet_NLoS(ACK_PACKET_NLoS,"NLoS",MACAP.currentSector)
                            if latency != None and data_rate != None:
                                RESULT_LATENCY.append(latency)
                                RESULT_DATA_RATE.append(data_rate)
                                RESULT_UE_ID.append(MACUE_device.ue_device.id)


            PACKETS_Logging.append(CTA_PACKET)
            PACKETS_Logging += RTS_PACKETS
            PACKETS_Logging.append(CTS_PACKET)
            PACKETS_Logging += UL_PACKETS
            PACKETS_Logging+=(ACK_Packets)
            logger.log_action(MESSAGES_Logging)
            
            for packet in PACKETS_Logging:
                if(packet == None):
                    continue
                logger.log_packet(packet)

            simulationTotalTimeElapsed += LoS_Sector_Time + nLos_Sector_Time
            
            apSector += 1
            if(apSector > self.AP.number_of_sectors):
                apSector = 1
                # cycle_period.append(((ACK_PACKETS.timeStampTransmission-simulationTotalTimeElapsed) + MAC_Controller.SectorTransitionTimeDelay))
            MACAP.currentSector = apSector
            if simulationTotalTimeElapsed > endTime:
                break

        
        print("RTS Rate Of Failure: " + str(RTS_Failures / Total_RTS))
        print("NLoS UL Rate Of Failure: " + str(NLoS_UL_failures / NLOS_Total_UL_Packets))
        print("Total UL Packets NLoS: " + str(NLOS_Total_UL_Packets))
        print("Failed UL Packets NLoS: " + str(NLoS_UL_failures))
        # print("\n\n Mean Cycle Period \n\n " +str(np.mean(cycle_period) * self.AP.number_of_sectors) + "Sec")
        return RESULT_LATENCY, RESULT_DATA_RATE, RESULT_UE_ID,NLoS_Path_Mapping
 





