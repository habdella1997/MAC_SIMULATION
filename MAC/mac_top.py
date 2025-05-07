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
from results import Results_Data
import constants
#packet sizes in bytes.
import random


class MAC_Controller:
    # Misc Control Params
    AP_STARTING_SECTOR        = 0     # Sector in which AP begin upon start of simulation 
    BOUNDARY_OF_ROOM          = 0.1   # Used to limit the loaction of UE handset to not be very close or on the room edge 
    UE_MAX_RETRANSMISSION     = 10    # Limits the number of Transmissions
    SectorTransitionTimeDelay =  0    #1*(10**-9)  #2 *(10**-6) # [nS] time to move from one sector to another 

    #Packet Params
    CONTROL_PACKET_SIZE  = 24    #bytes
    CONTROL_PACKET_BEFF  = 2     #bandwidth effeciency for QPSK
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
    def __init__(self, mac_protocol, systemBandwidth, room:room2, maxNumUEDevices):
        self.mac_protocol        = mac_protocol
        self.sectorTime          = 0
        self.simRoom             = room
        self.bandwidth           = systemBandwidth
        self.AP                  = []
        
        self.control_BW          = None
        self.data_BW             = None
        self.sectorTime          = None
        self.blockage            = False
        self.turnDelay           = False
        self.turnTimeDelay       = 0
        
        

        # Used to Compute New Packet Sizes based on Coding Scheme Utilized. <- Defined in packetEncoding()
        self.controlPacketLength_Encoded           = 0
        self.controlPacketTransmissionRate_Encoded = 0
        self.controlPacketTransmissionRate_Encoded_RTS = 0
        self.dataPacketLength_Encoded              = 0
        
        self.UE_List             = []
        self.MACUEDevices        = []
        self.ue_coordinates      = None
        self.maxNumUEDevices     = maxNumUEDevices
        self.maxUEXcord          = None
        self.maxUEYcord          = None
        self.UERandomBackOffTime = 0.01e-6
        
        self.reuseSetup          = False #used for allowing simulator to reuse the setup UE from previous simulation (cuts time)
        self.fixedUEObject       = None  #stores the UE objects;

    # TOP LEVEL Function for seting up the MAC
    # NumAP : Number of AP units: Currently only supporting one AP per simulation
    # numUE : Number of UE units
    # beamwidth : beamdWidth in degrees -> used to compute the antenna gain, and number of sectors. 
    # UE_Power: UE Transmit Power in watts 
    # AP_Power: AP Transmit Power in watts
    # frequency: Center Frequency 
    # UE_uplinkTransmissionRate: The transmission rate of UE. Used to compute the transmission time. A higher value means the UE will be more likely to transmit a packet.  
    def setupMAC(self,numAP, lambda_density, AP_BeamWidth,UE_BeamWidth, UE_Power, AP_Power,frequency, lambda_transmission,startTime,simEndTime,logger:Logger,reflectors):
        if(self.reuseSetup):
            self.setup_devices_previous_run(self.AP, self.MACUEDevices, lambda_transmission)
        else:
            self.setup_devices(numAP, lambda_density, AP_BeamWidth,UE_BeamWidth, UE_Power, AP_Power,frequency, lambda_transmission, startTime,simEndTime)
            self.simRoom.setup_reflectors_in_room(reflectors)
            self.simRoom.setup_fov_generic(self.AP)
            self.los_linkbudget()
            self.packetEncoding()
        NLoSReflections         = None
        MAC_results             = None
        if(self.mac_protocol == constants.adaptMacLabel):
            MAC_results,NLoSReflections                 = self.macAdapt(logger,simEndTime)
        else:
            MAC_results,NLoSReflections = self.macOmni(logger,simEndTime)
        return MAC_results,NLoSReflections
 
    def collision_detection_ul(self,packets,MESSAGES_Logging):
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
                if (next_packet == packet or sender == next_packet.sender ):
                    continue
                arrival_time_next_packet  = next_packet.timeStampTransmission + next_packet.propagationDelay
                occupied_time_next_packet = arrival_time_next_packet + next_packet.transmissionDelay
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
                # MESSAGES_Logging.append("Packet ( " + packet.linkType + " )" + packet.packetType + "with seq id: " + str(packet.sequence_id)+ " occured no collision")
                # MESSAGES_Logging.append("UE device: " + str(packet.sender) + " sent Packet w/ no collision")
            else:
                if(sender == sender_next_packet):
                    print(packet.packetType)
                    print("UE colliding w/ itself bug present")
                    sys.exit(1)
                packets_dropped.append(packet)
                # MESSAGES_Logging.append("Packet ( " + packet.linkType + " )" + packet.packetType +"  with seq id: " + str(packet.sequence_id) +", "+ str(next_packet.sequence_id) +"has been dropped due to collision")
                # MESSAGES_Logging.append("UE device: " + str(packet.sender) + ", and UE Device: " + str(next_packet.sender) + " sent Packets that collided with one another")
                # MESSAGES_Logging.append("First Packet Transmission and Arrival Times are: " + str(packet.timeStampTransmission) + ", " +str(packet.timeStampArrival))
                # MESSAGES_Logging.append("First Packet Transmission and Arrival Times are: " + str(next_packet.timeStampTransmission) + ", " +str(next_packet.timeStampArrival))
        return packets_dropped,packets_success
        
    def setup_devices_previous_run(self, AP, UE_List, transmission_rate):
        self.AP = AP
        new_list = []
        #for ue_device in self.UE_List: MAC_UEDEVICES.append(mac_ue.macUE(ue_device))
        for ue_device in UE_List:
            # create a new UE object with the same coordinates in the UE_List:
            UE_DEVICE_NEW = UE.UE(ue_device.ue_device.xCor,
                                  ue_device.ue_device.yCor,
                                  MAC_Controller.UE_MAX_RETRANSMISSION,
                                  ue_device.ue_device.RFBox,
                                  transmission_rate,
                                  ue_device.ue_device.startTime,
                                  ue_device.ue_device.simEndTime)
            #Copy the MAC Setup of the UE_Device
            UE_DEVICE_NEW.setupUE()
            UE_DEVICE_NEW.connect_to_AP(self.AP)
            MAC_UE_NEW = mac_ue.macUE(UE_DEVICE_NEW)
            MAC_UE_NEW.NLoS_Signal = ue_device.NLoS_Signal
            MAC_UE_NEW.NLoS_p_rx   = ue_device.NLoS_p_rx
            MAC_UE_NEW.NLoS_max_data_rate = ue_device.NLoS_max_data_rate
            MAC_UE_NEW.NLoS_total_distance = ue_device.NLoS_total_distance
            MAC_UE_NEW.NLoS_Setup = ue_device.NLoS_Setup
            new_list.append(MAC_UE_NEW)
        self.MACUEDevices = new_list
    
    
    #Modify to incorporate fixed Coordinates + setup resuse...
    def setup_devices(self, numAP, lambda_density, AP_beamWidth,UE_BeamWidth, UE_Power, AP_Power,frequency, lambda_transmission,startTime,simEndTime):
        #Top Function to Setup the UE Device handset and AP
        AP_RFBox, UE_RFBox = RF.setup_RFEquipment(AP_beamWidth,UE_BeamWidth, UE_Power, AP_Power, frequency, self.bandwidth) # get the gain of the system. 
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
            # print("Expected Nodes: ")
            # print(expected_nodes)
            # print(MAC_Controller.BOUNDARY_OF_ROOM)
            radius = (self.simRoom.length - (MAC_Controller.BOUNDARY_OF_ROOM*self.simRoom.length))
            if(self.maxNumUEDevices != None and expected_nodes > self.maxNumUEDevices):
                expected_nodes = self.maxNumUEDevices
            if(self.maxUEXcord != None and radius > self.maxUEXcord):
                radius = self.maxUEXcord
            ue_coordinates = math_toolkit.randomCoordinates(expected_nodes, radius)
            self.ue_coordinates = ue_coordinates

        #Setup UE Devices: 
        for i, (x, y) in enumerate(ue_coordinates, 1):
            UE_DEVICE = UE.UE(x,y,MAC_Controller.UE_MAX_RETRANSMISSION,UE_RFBox,lambda_transmission,startTime,simEndTime)
            UE_DEVICE.setupUE()
            UE_DEVICE.connect_to_AP(self.AP)
            self.UE_List.append(UE_DEVICE)
            MAC_UE_NEW = mac_ue.macUE(UE_DEVICE)
            if(self.control_BW != None):
                MAC_UE_NEW.ue_device.RFBox.splitBandwidth(self.control_BW, self.data_BW)
            self.MACUEDevices.append(MAC_UE_NEW)


    def los_linkbudget(self):
        '''
        Computes the Maxiumim Distance that is supported by the RF Conditions set in the simulation
        '''
        d_support = channel.max_distance(self.AP.RFBox.power , 
                                         self.bandwidth, 
                                         self.AP.RFBox.gain, 
                                         self.MACUEDevices[0].ue_device.RFBox.gain, 
                                         self.AP.RFBox.frequency)
        MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT = self.simRoom.width
        self.d_support = d_support
        if(d_support < self.simRoom.width):
            print("Failure -> Room Distance is greater than channel support")
            sys.exit(1)
        else: 
            pass

    def packetEncoding(self):
        control_packet_length    = MAC_Controller.CONTROL_PACKET_SIZE * 8 #convert to bits
        data_packet_length       = MAC_Controller.PAYLOAD_PACKET_SIZE * 8
        
        control_length_encoded   = math.ceil(control_packet_length / MAC_Controller.FEC_NUMERATOR) * MAC_Controller.FEC_DENOMINATOR
        payload_length_encoded   = math.ceil(data_packet_length / MAC_Controller.FEC_NUMERATOR) * MAC_Controller.FEC_DENOMINATOR

        control_transmission_rate     = 0         
        if(self.mac_protocol == constants.omniMacLabel and self.control_BW != None):
            control_transmission_rate =  self.control_BW     * self.CONTROL_PACKET_BEFF
        else:
            control_transmission_rate =  self.bandwidth * self.CONTROL_PACKET_BEFF

        self.controlPacketLength_Encoded           = control_length_encoded
        self.controlPacketTransmissionRate_Encoded = control_transmission_rate
        self.dataPacketLength_Encoded              = payload_length_encoded
    
    def return_devices(self):
        return self.AP, self.UE_List, self.MACUEDevices  
    def processingTimeDelay(self):
        pass
        # #Processing Time Delay Setup
        # BASEBAND_CLOCKING = 128e6
        # PERCENTAGE_OF_TIME_DELAY = 0.2
        # if(self.Processing_Delay_Accounted):
        #     PROCESSING_TIME_PACKET_control = newPacket_length * (1/BASEBAND_CLOCKING) * PERCENTAGE_OF_TIME_DELAY
        # else:
        #     PROCESSING_TIME_PACKET_control = 0




    def macAdapt(self, logger:Logger, endTime):
        print("ADAPT Simulation Start")
        print("Simulation End Time: " + str(endTime))
        sectorTimeElapsed = 0
        apSector = 0 # need to define Sector from here since its Dynamic
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
        MAC_Results = Results_Data(self.AP.number_of_sectors)
        PROCESSING_TIME_PACKET_control = 0
        UE_ID_in_Simulation = [x.ue_device.id for x in MAC_UEDEVICES]
        NLoS_Path_Mapping   = dict((key,[[],[]]) for key in UE_ID_in_Simulation)
        simulation_iteration_counter = 0
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
            # MACUE_devices_withTransmission_Request = []

            RTS_PACKETS,MACUE_devices_withTransmission_Request = self.setup_RTS_packets(
                                                                                                total_wait_time, # Sector End Time
                                                                                                constants.LoS, #Link Type
                                                                                                [], #Logging Purposes
                                                                                                MAC_UEDEVICES,
                                                                                                CTA_PACKET, 
                                                                                                MACAP,
                                                                                                self.simRoom,
                                                                                                1
                                                                                            )
            
            
            RTS_DROPPED,RTS_SUCCESS = self.collision_detection_ul2(RTS_PACKETS,[])

            RTS_Failures += len(RTS_DROPPED)
            Total_RTS += len(RTS_PACKETS)

            for dropped_packet in RTS_DROPPED:
                for device in MACUE_devices_withTransmission_Request:
                    if dropped_packet.sender == device.ue_device.id:
                        device.process_RTS_collision(constants.LoS)

            RTS_PACKETS = RTS_SUCCESS


            if(len(RTS_PACKETS)==0): #No Transmission Needed in this in time slot
                simulationTotalTimeElapsed += (max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay + self.turnTimeDelay)
                apSector += 1
                if(apSector >= self.AP.number_of_sectors):
                    cycle_period.append(max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay)
                    apSector = 0
                MACAP.currentSector = apSector
                logger.log_packet(CTA_PACKET)
                if simulationTotalTimeElapsed > endTime:
                    break
                continue



            CTS_PACKET = MACAP.create_CTS_Packet_ADAPT(RTS_PACKETS,
                                                 MAC_Controller.MAX_DISTANCE_CONTROL_SUPPORT,
                                                 total_wait_time)
            
            if len(CTS_PACKET.allocatedTimeSlots) == 0:
                simulationTotalTimeElapsed += (max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay + self.turnTimeDelay)
                apSector += 1
                if(apSector >= self.AP.number_of_sectors):
                    cycle_period.append(max_time_elapsed_CTA + max_time_elapsed_RTS + RANDOM_BACK_OFF_TIME_MAX + MAC_Controller.SectorTransitionTimeDelay)
                    apSector = 0
                MACAP.currentSector = apSector
                logger.log_packet(CTA_PACKET)
                if simulationTotalTimeElapsed > endTime:
                    break
                continue

            UL_PACKETS  = []
            for MACUE_device in MACUE_devices_withTransmission_Request:
                UL_PACKET = MACUE_device.process_CTS_packet_ADAPT(CTS_PACKET,apSector)
                if(UL_PACKET != None):
                    UL_PACKETS.append(UL_PACKET)
            

   
            ACK_PACKETS = MACAP.create_ACK_Packet(UL_PACKETS)



            for MACUE_device in MACUE_devices_withTransmission_Request:
                latency, data_rate = MACUE_device.process_ACK_packet(ACK_PACKETS,apSector)
                if latency != None and data_rate != None:
                    MAC_Results.add_results(latency,data_rate, MACUE_device.ue_device.id)
            
            PACKETS_Logging.append(CTA_PACKET)
            PACKETS_Logging += RTS_PACKETS
            PACKETS_Logging.append(CTS_PACKET)
            PACKETS_Logging += UL_PACKETS
            PACKETS_Logging.append(ACK_PACKETS)
            
            for packet in PACKETS_Logging:
                if(packet == None):
                    continue
                logger.log_packet(packet)

            simulationTotalTimeElapsed += ((ACK_PACKETS.timeStampTransmission-simulationTotalTimeElapsed) + MAC_Controller.SectorTransitionTimeDelay+ self.turnTimeDelay) 
            apSector += 1
            if(apSector > self.AP.number_of_sectors):
                apSector = 0 
                cycle_period.append(((ACK_PACKETS.timeStampTransmission-simulationTotalTimeElapsed) + MAC_Controller.SectorTransitionTimeDelay))
            MACAP.currentSector = apSector
            if simulationTotalTimeElapsed > endTime:
                break
        
        print("RTS Rate Of Failure: " + str(RTS_Failures / Total_RTS))
        print("\n\n Mean Cycle Period \n\n " +str(np.mean(cycle_period) * self.AP.number_of_sectors) + "Sec")
        return MAC_Results, NLoS_Path_Mapping




    def setup_RTS_packets(self,sectorEndTime, linkType,MESSAGES_Logging,MAC_UEDEVICES,CTA_PACKET,MACAP,simRoom, numOfRequestesPermitted = None): # Verified - Hussam
        MACUE_devices_withTransmission_Request = []
        RTS_PACKETS = []
        if(linkType == constants.LoS):
            for device in MAC_UEDEVICES:
                ue_device_sector = device.return_UE_Sector()
                if(ue_device_sector == MACAP.currentSector): #LoS Condition 
                    CTA_PACKET.addRecepients(device.ue_device.id)
                    device.process_CTA_packet(CTA_PACKET)
                    # MESSAGES_Logging.append("LoS CTA Received by UE: " + str(device.ue_device.id) + 
                    #                         " sitting at sector: " + str(ue_device_sector) +
                    #                         " at time: " + str(device.lastCTA_ArrivalTime) + 
                    #                         ", at sector " + str(MACAP.currentSector))
                    if(device.check_Transmission_Capbaility(sectorEndTime,MACAP.currentSector,constants.LoS,MACAP,simRoom,MESSAGES_Logging)):
                        # MESSAGES_Logging.append("UE has something to transmit")
                        MACUE_devices_withTransmission_Request.append(device)
                        UL_Valid_Transmissions = device.ue_device.check_number_packets(sectorEndTime)
                        # MESSAGES_Logging.append("Packet Time slots that pass the time criteria: "+ str(' '.join(map(str, UL_Valid_Transmissions))))
                        last_RTS_Packet = None
                        requests_made = 0
                        for transmissions in UL_Valid_Transmissions:
                            if(self.mac_protocol == constants.adaptMacLabel):
                                RTS_PACKET = None
                                if(transmissions < device.lastCTA_ArrivalTime):
                                    RTS_PACKET = device.create_RTS_Packet(constants.LoS,device.lastCTA_ArrivalTime,MACAP.currentSector,last_RTS_Packet)
                                else:
                                    RTS_PACKET = device.create_RTS_Packet(constants.LoS,transmissions,MACAP.currentSector,last_RTS_Packet)
                                if self.blockage:
                                    blockage_prob = channel.compute_propabilityLoS_indoorMixed(RTS_PACKET.distance)
                                    threshold_pr  = math_toolkit.random_uniform_between(0,1)
                                    if(threshold_pr <= blockage_prob):
                                        break
                                RTS_PACKETS.append(RTS_PACKET)
                                break
                            else:
                                RTS_PACKET = device.create_RTS_Packet(constants.LoS,transmissions,MACAP.currentSector,last_RTS_Packet)
                                last_RTS_Packet = RTS_PACKET
                                # MESSAGES_Logging.append("RTS PACKET created with seq id: " + str(RTS_PACKET.sequence_id))
                                if self.blockage:
                                    blockage_prob = channel.compute_propabilityLoS_indoorMixed(RTS_PACKET.distance)
                                    threshold_pr  = math_toolkit.random_uniform_between(0,1)
                                    if(threshold_pr <= blockage_prob):
                                        continue 
                                RTS_PACKETS.append(RTS_PACKET)
                    else:
                        pass
        else:
            for device in MAC_UEDEVICES: 
                    if(device.check_Transmission_Capbaility(sectorEndTime,MACAP.currentSector,constants.NLoS,MACAP,simRoom,MESSAGES_Logging)):
                        device.process_CTA_packet(CTA_PACKET) #Not actually receiving a CTA, but need it to flush the MACUE system-removing this will impact the MAC ue NloS Transmission time           
                        # MESSAGES_Logging.append("NLoS For UE ID: " + str(device.ue_device.id) + "and has something to transmit")        
                        MACUE_devices_withTransmission_Request.append(device)
                        UL_Valid_Transmissions = device.ue_device.check_number_packets(sectorEndTime)
                        last_RTS_Packet = None
                        for transmissions in UL_Valid_Transmissions:
                            RTS_PACKET = device.create_RTS_Packet(constants.NLoS,transmissions,MACAP.currentSector,last_RTS_Packet)
                            if(RTS_PACKET == None ):
                                break
                            if self.blockage:
                                blockage_prob = channel.compute_propabilityLoS_indoorMixed(RTS_PACKET.distance)
                                threshold_pr  = math_toolkit.random_uniform_between(0,1)
                                if(threshold_pr <= blockage_prob):
                                    continue
                            last_RTS_Packet = RTS_PACKET
                            # MESSAGES_Logging.append("RTS PACKET created with seq id: " + str(RTS_PACKET.sequence_id)) 
                            RTS_PACKETS.append(RTS_PACKET)
                    else:
                        pass
        return RTS_PACKETS,MACUE_devices_withTransmission_Request


    def setup_CTS_packets(self,RTS_PACKETS,MESSAGES_Logging,MACAP): #Verified - Hussam
        CTS_PACKET = None
        if(len(RTS_PACKETS)>0):
            if(self.mac_protocol == constants.omniMacLabel):
                CTS_PACKET = MACAP.create_CTS_Packet_OMNI(RTS_PACKETS)
                for indexer,grantsApproved in enumerate(CTS_PACKET.allocatedTimeSlots):
                    timeSlot = CTS_PACKET.allocatedTimeSlots[indexer]
                    ueID     = CTS_PACKET.allocatedUEID[indexer]
                    MESSAGES_Logging.append("UE : " + str(ueID) + ", has been alloacted the following time slot: " + str(timeSlot))
        return CTS_PACKET
    

    def setup_UL_packets(self,currentSector, CTS_PACKET,MACUE_devices_withTransmission_Request,MESSAGES_Logging,NLoS_Path_Mapping,sector_start_time,Sector_Time): # Verified - Hussam
        UL_PACKETS   = []
        NLoS_Signals = []
        AP_Sectors   = []
        if(CTS_PACKET != None):
            for device in MACUE_devices_withTransmission_Request:
                for indexer,ue_ID in enumerate(CTS_PACKET.allocatedUEID):
                    if device.ue_device.id == ue_ID:
                        UL_PACKET, NLoS_Signal,AP_Sector = device.process_CTS_packet(CTS_PACKET,sector_start_time,currentSector,Sector_Time)
                        UL_PACKETS = UL_PACKETS + UL_PACKET
                        AP_Sectors = AP_Sectors + AP_Sector
                        for index,pck in enumerate(UL_PACKET):
                            if(pck.linkType == constants.NLoS and NLoS_Signal[index] != None): 
                                NLoS_Path_Mapping[device.ue_device.id][0].append(pck.timeStampTransmission)
                                NLoS_Path_Mapping[device.ue_device.id][1].append(NLoS_Signal[index])
                            MESSAGES_Logging.append("UEID: " + str(ue_ID) + "generated the following ul packet: " + str(pck.sequence_id))
                        break
            
        return UL_PACKETS, NLoS_Signals, AP_Sectors

    def setup_ACK_packets(self,UL_PACKETS,MACAP, APSectors): # Verified - Hussam
        ACK_Packets = []     
        for index,UL_Packet in enumerate(UL_PACKETS):
            ACK_Packet = MACAP.create_ACK_PacketNLoS(UL_Packet,APSectors[index])
            ACK_Packets.append(ACK_Packet)
        return ACK_Packets 
    

    def handle_RTS_Collisions(self, collided_packets, MACUE_Devices, sectorEndTime): #Verified - Hussam {Can be optimized to scale w/ increasing number of devices O(n^2) -> O(n)}
        new_RTS_packets = [] 
        for mac_ue_device in MACUE_Devices:
            for rts_packet in collided_packets: 
                if rts_packet.sender == mac_ue_device.ue_device.id:
                    mac_ue_device.process_RTS_collision(rts_packet.linkType)
                    wait_time_before_collision_awarness = (2*rts_packet.transmissionDelay + 2*rts_packet.propagationDelay)
                    transmission_time_of_rts     = rts_packet.timeStampTransmission
                    new_transmission_time_of_rts = transmission_time_of_rts + wait_time_before_collision_awarness + mac_ue_device.compute_RANDOMBACKOFF_time()
                    if(new_transmission_time_of_rts < sectorEndTime):
                        continue
                    rts_packet.timeStampTransmission = new_transmission_time_of_rts
                    rts_packet.settimeStampArrival()
                    new_RTS_packets.append(rts_packet)
        return new_RTS_packets

                

    def macOmni(self, logger:Logger, endTime):
        # print("MAC-OMNILLUSION Simulation Has Began - Good Luck :) ")
        # print("Simulation End Time: " + str(endTime))
        
        Sector_Time         = self.sectorTime
        apSector            = self.AP_STARTING_SECTOR
        
        # PARAMETERS:
        RANDOM_BACK_OFF_TIME_MAX = self.UERandomBackOffTime
        
        mac_ue.macUE.RANDOM_BACKOFF_MAXTIME =  RANDOM_BACK_OFF_TIME_MAX
        mac_ue.macUE.RANDOM_BACKOFF_MINTIME = 0

        
        #create MAC_UE objects for each UE

        
        #Simulation LOOP Variables
        simulationTotalTimeElapsed = 0
        if(self.control_BW != None):
            self.AP.RFBox.splitBandwidth(self.control_BW, self.data_BW)
        MACAP = mac_ap.macAP(self.AP,apSector)
        MACAP.AP.sectorTime = self.sectorTime

        Packet.CONTROL_PACKET_LENGTH = self.controlPacketLength_Encoded 
        Packet.CONTROL_PACKET_RATE   = self.controlPacketTransmissionRate_Encoded
        Packet.DATA_PACKET_LENGTH    = self.dataPacketLength_Encoded
        
        #Results:
        MAC_Results = Results_Data(self.AP.number_of_sectors)

        utilities.status = 0  
        MAC_UEDEVICES = self.MACUEDevices
        UE_ID_in_Simulation = [x.ue_device.id for x in MAC_UEDEVICES]
        NLoS_Path_Mapping   = dict((key,[[],[]]) for key in UE_ID_in_Simulation)
        simulation_iteration_counter = 0
        RTS_Failures = 0
        Total_RTS    = 0
        
        while True:
            #utilities.print_status(simulationTotalTimeElapsed,endTime)
            PACKETS_Logging  = []
            MESSAGES_Logging = [] 
            sector_start_time = simulationTotalTimeElapsed
            
            # MESSAGES_Logging.append("Simulation Iteration Number: " + str(simulation_iteration_counter))
            # MESSAGES_Logging.append("Current Time: " + str(sector_start_time))
            # MESSAGES_Logging.append("AP is pointing at Sector: " + str(MACAP.currentSector))

            # ASK AP to create the CTA Packet and time-stamp it
            CTA_PACKET = MACAP.create_CTA_Packet(simulationTotalTimeElapsed,MACAP.currentSector)
            
    
            RTS_PACKETS_LoS,MACUE_devices_withTransmission_Request_LoS = self.setup_RTS_packets(
                                                                                                sector_start_time+(Sector_Time), # Sector End Time
                                                                                                constants.LoS, #Link Type
                                                                                                MESSAGES_Logging, #Logging Purposes
                                                                                                MAC_UEDEVICES,
                                                                                                CTA_PACKET, 
                                                                                                MACAP,
                                                                                                self.simRoom,
                                                                                            )
                                                                                        
            RTS_PACKETS_NLoS,MACUE_devices_withTransmission_Request_NLoS = self.setup_RTS_packets(
                                                                                                    sector_start_time+(Sector_Time),
                                                                                                    constants.NLoS,
                                                                                                    MESSAGES_Logging,
                                                                                                    MAC_UEDEVICES,CTA_PACKET,
                                                                                                    MACAP,
                                                                                                    self.simRoom,
                                                                                                    
                                                                                                    )
            
            RTS_PACKETS = RTS_PACKETS_LoS + RTS_PACKETS_NLoS
            MACUE_devices_withTransmission_Request = MACUE_devices_withTransmission_Request_LoS + MACUE_devices_withTransmission_Request_NLoS
            
            # MAC_Results.add_sector_activity_RTS(MACAP.currentSector, len(RTS_PACKETS))
            
            # Now we have all the RTS PACKETS. Lets drop the ones with collisions 
            RTS_DROPPED,RTS_SUCCESS = self.collision_detection_ul(RTS_PACKETS,MESSAGES_Logging)
            RTS_Failures += len(RTS_DROPPED)
            Total_RTS    += len(RTS_PACKETS)
            
            # MESSAGES_Logging.append("Total RTS Packets: " + str(len(RTS_PACKETS)) + ", Dropped RTS packets: " + str(len(RTS_DROPPED)))
            
            # MAC_Results.add_collision_RTS(len(RTS_DROPPED),len(RTS_PACKETS) )
            RTS_PACKETS = RTS_SUCCESS
            
            PROCESSED_RTS_PACKETS = self.handle_RTS_Collisions(RTS_DROPPED, MACUE_devices_withTransmission_Request, sector_start_time+Sector_Time)
            re_transmission_counter =0
            while(len(PROCESSED_RTS_PACKETS) > 0):
                re_transmission_counter +=1
                if(re_transmission_counter>4):
                    print(re_transmission_counter)
                RTS_PACKETS = RTS_PACKETS + PROCESSED_RTS_PACKETS
                RTS_DROPPED,RTS_SUCCESS = self.collision_detection_ul(RTS_PACKETS,MESSAGES_Logging)
                MAC_Results.add_collision_RTS(len(RTS_DROPPED),len(RTS_PACKETS) )
                RTS_PACKETS = RTS_SUCCESS
                # MESSAGES_Logging.append("Re-Transmission Attempt: " + str(re_transmission_counter))
                # MESSAGES_Logging.append("Total RTS Packets: " + str(len(RTS_PACKETS)) + ", Dropped RTS packets: " + str(len(RTS_DROPPED)))  
                PROCESSED_RTS_PACKETS = self.handle_RTS_Collisions(RTS_DROPPED,MACUE_devices_withTransmission_Request,sector_start_time+Sector_Time)

            CTS_PACKET = self.setup_CTS_packets(RTS_PACKETS,
                                                MESSAGES_Logging,
                                                MACAP)
            
            
            UL_PACKETS,dontcare,APSectors = self.setup_UL_packets(
                                                        MACAP.currentSector,
                                                        CTS_PACKET,
                                                        MACUE_devices_withTransmission_Request,
                                                        MESSAGES_Logging,
                                                        NLoS_Path_Mapping,
                                                        sector_start_time,
                                                        Sector_Time
                                                        )

            # for apSector_log in range (0,MACAP.AP.number_of_sectors):
            #     MAC_Results.add_sector_activity_UL(apSector_log, APSectors.count(apSector_log))
            
            ACK_Packets = self.setup_ACK_packets(UL_PACKETS,MACAP, APSectors)

            for MACUE_device in MACUE_devices_withTransmission_Request:
                for ACK_Packet in ACK_Packets:
                    if(MACUE_device.ue_device.id == ACK_Packet.ueIDlist[0]):
                        # MESSAGES_Logging.append("UEID : "+str(MACUE_device.ue_device.id) + "has receieved an ACK")
                        latency, data_rate = MACUE_device.process_ACK_packet_NLoS(ACK_Packet,sector_start_time,MACAP.currentSector,Sector_Time)
                        # MESSAGES_Logging.append("Latency For Transaction: " + str(latency))
                        # MESSAGES_Logging.append("Tput for transaction: " + str((self.dataPacketLength_Encoded / latency)/1e9))
                        if(latency < 0 ):
                            print("Latency Error less than 0")
                            sys.exit(1)
                        if latency != None and data_rate != None:
                            MAC_Results.add_results(latency,data_rate, MACUE_device.ue_device.id)

            # PACKETS_Logging.append(CTA_PACKET)
            # PACKETS_Logging += RTS_PACKETS
            # PACKETS_Logging.append(CTS_PACKET)
            # PACKETS_Logging += UL_PACKETS
            # PACKETS_Logging+=(ACK_Packets)
            # logger.log_action(MESSAGES_Logging)
            
            # for packet in PACKETS_Logging:
            #     if(packet == None):
            #         continue
            #     logger.log_packet(packet)

            simulationTotalTimeElapsed += Sector_Time 
            
            apSector += 1
            simulation_iteration_counter +=1
            if(apSector >= self.AP.number_of_sectors):
                apSector = 0
            MACAP.currentSector = apSector
            if simulationTotalTimeElapsed > endTime:
                break
        print("RTS Failure Rate: " + str((RTS_Failures/Total_RTS)*100))
        # logger.store_packets()
        return MAC_Results, NLoS_Path_Mapping
    

