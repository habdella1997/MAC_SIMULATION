import channel 
import math
import Objects.UE as UE
import Objects.AP as AP
from typing import List
import math_toolkit
from Objects.transmission2 import * 
from room2 import room2
import Objects.mirror as mirror
import plotter
import sys
import constants
import random
# Moving from the UE object to MAC Ue -> More applicable to have here. 
# 
# def findmySector(self):
#         return self.AP.return_mySector(self.xCor, self.yCor)




class macUE:
    RANDOM_BACKOFF_MAXTIME = 0.8e-6
    RANDOM_BACKOFF_MINTIME = 0


    def __init__(self, UE:UE.UE):
        self.ue_device = UE
        self.mySector = None
        self.distanceToAP = None
        self.lastCTA_ArrivalTime = None
        self.ULGrants = []
        self.ULGrantIndex = 0
        self.ULGrantACKIndex = 0
        self.retransmissions = 0

        self.NLoS_Signal         = [None for x in range(UE.AP.number_of_sectors)]
        self.NLoS_p_rx           = [None for x in range(UE.AP.number_of_sectors)]
        self.NLoS_max_data_rate  = [None for x in range(UE.AP.number_of_sectors)]
        self.NLoS_total_distance = [None for x in range(UE.AP.number_of_sectors)]
        self.NLoS_Setup          = [False for x in range(UE.AP.number_of_sectors)]
        self.NLoS_init           = False 
    
    def update_sector(self):
        # Updates the sector in which UE is in. 
        # Needs to be called at every step in the simulation in case of UE movement. 
        # If mobility is deactivated, calling this once in the beginnign should suffice 
        x = self.ue_device.xCor
        y = self.ue_device.yCor
        ueSector = self.ue_device.AP.return_mySector(x,y)
        dist_to_ap = math_toolkit.euclidean_distance(self.ue_device.AP.xCor, self.ue_device.AP.y, x,y)
        self.ue_device.mySector = ueSector
        self.ue_device.distanceToAP = dist_to_ap
        self.ue_device.propagationDelay = channel.compute_propagationDelay(dist_to_ap)
        self.mySector     = ueSector
        self.distanceToAP = dist_to_ap
        
        
    
    def return_UE_Sector(self):
        self.update_sector()
        return self.mySector

    # Called From the MAC TOP Level
    # Two Conditions need to be Met
    # 1. UE needs to transmit {Time of tranmission <= current time}
    # 2. UE needs to be capbale of establishing a link with AP -> {LoS / NLoS}
    def check_Transmission_Capbaility(self,endTime,apSector, linkType,MACAP,simRoom,MESSAGES_Logging):
        if simRoom.MIRRORS != None and self.NLoS_init == False:
            self.setupNLoSLinks(MACAP.AP,simRoom)
        if(self.ue_device.check_for_transmission(endTime)):#self.lastCTA_ArrivalTime+time_window_right)):
            if(linkType == constants.LoS ):
                if(self.mySector == apSector):
                    return True
                else:
                    return False
            elif(linkType == constants.NLoS):
                if(self.mySector != apSector):
                    if(self.NLoS_Signal[MACAP.currentSector] == None or self.NLoS_Signal[MACAP.currentSector].NLoS ==0):
                        print("Sector: " + str(MACAP.currentSector))
                        print("UE cords: ")
                        print([self.ue_device.xCor,self.ue_device.yCor])
                        print("No NLoS Available - should not happen")
                        sys.exit(1)
                        MESSAGES_Logging.append("UE Node Has something to transmit, but nLoS Aint available")
                        return False
                    if(self.NLoS_max_data_rate[MACAP.currentSector] == 0): #weak NLoS Link Non-existant
                        return False
                    return True 
                else:
                    return False
        return False

    def OmniMAC_RTSTransmissionTime(self,endtime,startPercentage):
        return math_toolkit.random_uniform_between(endtime*startPercentage,endtime)
    
    def process_RTS_collision(self, linkType):
        #if(linkType ==constants.LoS):
        self.retransmissions = self.retransmissions + 1    

        

    def check_done_transmissions(self):
        return self.ue_device.check_transmission_queue()

    def compute_RANDOMBACKOFF_time(self):
        return math_toolkit.random_uniform_between(macUE.RANDOM_BACKOFF_MINTIME,macUE.RANDOM_BACKOFF_MAXTIME) + (math_toolkit.random_uniform_between(0,2**self.retransmissions)*1e-9)

    def create_RTS_Packet(self,linkType,transmissionInstance,currentSector,prevRTSPacket): #UL_timeTable for MACHUSSAM -> need to integrate into ADAPT
        timeAdvance = 0
        small_time_delta = 2e-9
        #Avoid collision between the last RTS I sent, and the current RTS im about to send. 
        randomBackoffTime = self.compute_RANDOMBACKOFF_time()
        if(prevRTSPacket != None):
            if(transmissionInstance <= (prevRTSPacket.timeStampTransmission + prevRTSPacket.transmissionDelay + randomBackoffTime)):
                timeAdvance = (prevRTSPacket.timeStampTransmission + prevRTSPacket.transmissionDelay+ small_time_delta) - transmissionInstance
        RTS_packet = None
        actual_transmissionTime = transmissionInstance + timeAdvance + randomBackoffTime

        if linkType == constants.LoS:
            RTS_packet = RTS(self.ue_device.id, self.ue_device.AP.id,linkType)
            RTS_packet.setupTransmissionDelay()
            RTS_packet.setupPropagationDelay(self.distanceToAP)
            p_rx, max_data_rate, ber, modulation_scheme = -1,-1,-1,None
            RTS_packet.settimeStampTransmission(actual_transmissionTime)
            RTS_packet.settimeStampArrival()
            if(self.ue_device.RFBox.splitBandwidthValid):
                p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(self.ue_device.RFBox.power, 
                                                                                  self.distanceToAP, 
                                                                                  self.ue_device.AP.RFBox.dataBandwidth, 
                                                                                  self.ue_device.RFBox.gain +self.ue_device.AP.RFBox.gain , 
                                                                                  self.ue_device.AP.RFBox.frequency, 
                                                                                  0)
            else:
                p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(self.ue_device.RFBox.power, 
                                                                                  self.distanceToAP, 
                                                                                  self.ue_device.AP.RFBox.bandwidth, 
                                                                                  self.ue_device.RFBox.gain +self.ue_device.AP.RFBox.gain , 
                                                                                  self.ue_device.AP.RFBox.frequency, 
                                                                                  0)

            RTS_packet.setupLinkBudget(p_rx,max_data_rate, modulation_scheme)
            RTS_packet.setupULDuration(max_data_rate)
        else:
            # Need to move this to the AP, The RTS is sent, an AP decides the UL grant, the sector it will be in, and from there it should estimate the data-rate-
            NLoS_Signal_highest   = self.NLoS_Signal[currentSector]
            max_data_rate_highest = self.NLoS_max_data_rate[currentSector]
            distance              = self.NLoS_total_distance[currentSector]

            if NLoS_Signal_highest == None or NLoS_Signal_highest.NLoS == 0 or max_data_rate_highest == 0:
                return RTS_packet

            RTS_packet = RTS(self.ue_device.id, self.ue_device.AP.id,linkType)
            RTS_packet.setupTransmissionDelay()
            RTS_packet.setupPropagationDelay(distance)
            # this could cause collisons, if two consecutive links are drastically different in distance. Very unlikely but look into it later. 
            RTS_packet.settimeStampTransmission(actual_transmissionTime)
            RTS_packet.settimeStampArrival()
     
            RTS_packet.setupLinkBudget(self.NLoS_p_rx[currentSector],max_data_rate_highest, "Na.")
            RTS_packet.setupULDuration(max_data_rate_highest)
        RTS_packet.numberOfGrantsNeeded = 1
        return RTS_packet
        
    
    def create_ULDATA_Packet(self,linkType,currentSector,timeForTransmission,dataRate):
        # URGENTBUG - NEED TO TAKE THE TIME SLOT TO BE AFTER NEEDING TO TRANSMIT. 
        # THE WAY THIS IS CODED -> THE TIME SLOT ASSIGNED COULD POTENTIALLY BE BEFORE THE
        # UE EVEN REALIZED THAT IT HAS ANYTHIGN TO SEND.!.!!!!!!!!!!!!!!!!!!!!
        NLoS_Signal = None
        UL_DATA_PACKET = UL_DATA(self.ue_device.id, self.ue_device.AP.id,linkType)
        UL_DATA_PACKET.setupTransmissionDelay(dataRate)
        if(linkType==constants.LoS):
            UL_DATA_PACKET.setupPropagationDelay(self.distanceToAP)
        else:
            if(self.NLoS_max_data_rate[currentSector] == 0):
                return None, None
            UL_DATA_PACKET.setupPropagationDelay(self.NLoS_total_distance[currentSector])
        UL_DATA_PACKET.settimeStampTransmission(timeForTransmission)
        UL_DATA_PACKET.settimeStampArrival()
        self.ue_device.UE_TRANSMISSIONS.pending_transmission(UL_DATA_PACKET)
        return UL_DATA_PACKET,self.NLoS_Signal[currentSector]



    def setupNLoSLinks_helper(self,AP,currentSector,simRoom):
        # Step 1: Get Mirrors in my FoV
        my_mirrors = simRoom.mirrors_with_coverage(self.ue_device,currentSector)
        p_rx_highest, max_data_rate_highest, ber_highest,total_distance_highest= -1,-1,-1,-1
        NLoS_Signal_highest = None
        
        if(my_mirrors):
            for mirror in my_mirrors:
                NLoS_Signal = simRoom.setup_valid_reflection_vectors(self.ue_device,AP,currentSector, mirror)
                
                if (NLoS_Signal == None or NLoS_Signal.NLoS == 0):
                    continue
            
                incidence_distane = math_toolkit.euclidean_distance(self.ue_device.xCor,
                                                                    self.ue_device.yCor,
                                                                    NLoS_Signal.reflect_x,
                                                                    NLoS_Signal.reflect_y )
                reflection_distance = math_toolkit.euclidean_distance(NLoS_Signal.reflect_x,
                                                                      NLoS_Signal.reflect_y,
                                                                      AP.xCor,
                                                                      AP.yCor )
                total_distance = incidence_distane+reflection_distance

                p_rx, max_data_rate, ber, modulation_scheme = -1,-1,-1,None
                if(self.ue_device.RFBox.splitBandwidthValid):
                    p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(  self.ue_device.RFBox.power, 
                                                                                        total_distance, 
                                                                                        self.ue_device.AP.RFBox.dataBandwidth, 
                                                                                        self.ue_device.RFBox.gain +self.ue_device.AP.RFBox.gain , 
                                                                                        self.ue_device.AP.RFBox.frequency, 
                                                                                        0)
                else:
                    p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(  self.ue_device.RFBox.power, 
                                                                                        total_distance, 
                                                                                        self.ue_device.AP.RFBox.bandwidth, 
                                                                                        self.ue_device.RFBox.gain +self.ue_device.AP.RFBox.gain , 
                                                                                        self.ue_device.AP.RFBox.frequency, 
                                                                                        0)
                if(max_data_rate>max_data_rate_highest):
                    p_rx_highest = p_rx
                    max_data_rate_highest = max_data_rate
                    ber_highest = ber
                    modulation_scheme_highest = modulation_scheme
                    NLoS_Signal_highest = NLoS_Signal
                    total_distance_highest = total_distance
                    break

        self.NLoS_max_data_rate[currentSector] = max_data_rate_highest
        self.NLoS_p_rx[currentSector] = p_rx_highest
        self.NLoS_Setup[currentSector] = True
        self.NLoS_Signal[currentSector] = NLoS_Signal_highest
        self.NLoS_total_distance[currentSector] = total_distance_highest
        
    
    def setupNLoSLinks(self,AP,simRoom):
            for i in range(0, AP.number_of_sectors):
                if(self.NLoS_Setup[i] == False):
                    self.setupNLoSLinks_helper(AP,i,simRoom)
            self.NLoS_init = True
        
                

    def create_ULDATA_Packet_NLoS(self,TransmissionTime,NLoS_DataRate,NLoS_Distance):
        UL_DATA_PACKET = UL_DATA(self.ue_device.id, self.ue_device.AP.id)
        UL_DATA_PACKET.setupTransmissionDelay(NLoS_DataRate)
        UL_DATA_PACKET.setupPropagationDelay(NLoS_Distance)
        UL_DATA_PACKET.settimeStampTransmission(TransmissionTime)
        UL_DATA_PACKET.settimeStampArrival()
        self.ue_device.UE_TRANSMISSIONS.pending_transmission(UL_DATA_PACKET)
        return UL_DATA_PACKET
    
    def OMNIMAC_createULGrant(self,timeSlots):
        start_index = -1
        time_for_tranmsission = self.ue_device.UE_TRANSMISSIONS.check_earliest_transmission()
        for indexer,timeSlot in enumerate(timeSlots):
            if time_for_tranmsission >= timeSlot:
                start_index = indexer
                break
        if(start_index == -1): #my earliest transmission is beyond that of the time slots available. I do not need to send.
            self.lastULGrant = None
            return

        randomTimeSlot_pick = math_toolkit.random_uniform_between(start_index,len(timeSlots)-1)
        #self.retransmissions -= 1
        p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(self.ue_device.RFBox.power, 
                                                                              self.distanceToAP, 
                                                                              self.ue_device.AP.RFBox.bandwidth, 
                                                                              self.ue_device.RFBox.gain +self.ue_device.AP.RFBox.gain , 
                                                                              self.ue_device.AP.RFBox.frequency, 
                                                                                      0)
        grant_approved = UL_GRANT(timeSlots[randomTimeSlot_pick],max_data_rate)
        self.lastULGrant = grant_approved

        

    def process_CTA_packet(self,CTA:CTA):
        arrival_time = CTA.timeStampTransmission + channel.compute_propagationDelay(self.distanceToAP) + CTA.transmissionDelay
        CTA.setupPropagationDelay(self.distanceToAP, self.ue_device.id)
        CTA.settimeStampArrival(arrival_time)
        self.lastCTA_ArrivalTime = arrival_time

    
    def process_CTS_packet(self, CTS:CTS,sectorStartTime, currentSector, sectorTime):
        UL_PACKETS  = []
        NLoS_Signals = []
        if(self.retransmissions > 0):
            self.retransmissions -= 1
        
        arrival_time = 0
        if(self.mySector != currentSector):
            NLoS_Distance = self.NLoS_total_distance[currentSector]
            arrival_time = CTS.timeStampTransmission + channel.compute_propagationDelay(NLoS_Distance) + CTS.transmissionDelay
            CTS.setupPropagationDelay(NLoS_Distance, self.ue_device.id)
        else:    
            arrival_time = CTS.timeStampTransmission + channel.compute_propagationDelay(self.distanceToAP) + CTS.transmissionDelay
            CTS.setupPropagationDelay(self.distanceToAP, self.ue_device.id)
       
        CTS.settimeStampArrival(arrival_time)

        for i in range(len(CTS.allocatedTimeSlots)):
            if CTS.allocatedUEID[i] == self.ue_device.id:
                find_time_slot = CTS.allocatedTimeSlots[i]
                data_rate_approved = CTS.allocateddataRate[i]
                if(find_time_slot < self.ue_device.UE_TRANSMISSIONS.check_earliest_transmission()):
                    print("Error MAC UE CTS Packet Processing -> Grant Received Prior To UE need for transmission\n")
                    sys.exit(1)
                sector_forTransmission = self.ue_device.AP.find_current_sector(sectorStartTime, currentSector, sectorTime, find_time_slot)
                linkType = None
                if(sector_forTransmission == self.mySector):
                    linkType = constants.LoS
                else:
                    linkType = constants.NLoS 
                UL_PACKET, NLoS_Signal = self.create_ULDATA_Packet(linkType,sector_forTransmission,find_time_slot,data_rate_approved)
                if(UL_PACKET == None):
                    continue
                UL_PACKETS.append(UL_PACKET)
                if(linkType == constants.NLoS):
                    NLoS_Signals.append(NLoS_Signal)
                else:
                    NLoS_Signals.append(None)
        return UL_PACKETS, NLoS_Signals

    
    def process_ACK_packet(self, ACKs:ACK,currentSector):
        if(ACKs == None):
            return None,None
        if(self.ULGrants == None):
            return None,None
        latency = 0
        data_rate = 0
        for index,device_id in enumerate(ACKs.ueIDlist):
            if device_id == self.ue_device.id:
                    arrival_time = ACKs.timeStampTransmission + channel.compute_propagationDelay(self.distanceToAP) + ACKs.transmissionDelay
                    ACKs.settimeStampArrival(arrival_time)
                    ACKs.setupPropagationDelay(self.distanceToAP, self.ue_device.id)
                    timeOfPacketCreation, ul_packet = self.ue_device.transmission_succesful(ACKs.packetsACKED_UELIST[index],currentSector)
                    latency = arrival_time - timeOfPacketCreation
                    data_rate = ul_packet.dataRate
                    return latency,data_rate
        return None,None

    def process_ACK_packet_NLoS(self, ACKs:ACK,APSector ):
        #BUG_REPORT:
        #URGENT_Level_FUCKFUCKFUCK:(MEANING FIX ASAP)
        #IF UL Packet is dropped, you need to find related UL packet here and not remove it from the tranmission queue
        # The way this goes, I drop the latest of the qeue for every ack (THIS is fine LoS since there is no drops given the time slot approach)
        latency   = 0
        data_rate = 0
        arrival_time = 0
        
        timeOfPacketCreation, UL_packet = self.ue_device.transmission_succesful(ACKs.packetsACKED_UELIST[0],APSector)
        ack_distance = UL_packet.distance
        arrival_time = ACKs.timeStampTransmission + channel.compute_propagationDelay(ack_distance) + ACKs.transmissionDelay
        latency = arrival_time - timeOfPacketCreation
        data_rate = ACKs.NLoS_data_rate
        ACKs.settimeStampArrival(arrival_time)
        ACKs.setupPropagationDelay(self.distanceToAP, self.ue_device.id)

        return latency,data_rate
    
    def process_UL_PacketFailure(self, ulpacket,linkType,APSector):
        self.ue_device.UE_TRANSMISSIONS.transmit_failure(ulpacket.sequence_id,linkType,APSector)
        

    def link_budget_RTS(ue_device:UE.UE, AP:AP.AP):
        distance = math_toolkit.euclidean_distance(AP.x, AP.y, ue_device.xCor, ue_device.yCor)
        p_rx, max_data_rate, BER, modulation_scheme = channel.link_budget(ue_device.p_tx, distance, AP.bandwidth, ue_device.txGain+AP.rxGain, AP.f_c_UL, 0)
        return max_data_rate

    

    def requestMSC(UE_device:UE.UE, RTS_PACKET:RTS,ue_to_ap_distance):
        p_rx, max_data_rate, ber, modulation_scheme = channel.link_budget(UE_device.p_tx, ue_to_ap_distance, UE_device.AP.maxBandwidth, UE_device.txGain +UE_device.AP.rxGain , 
                                                                                                UE_device.AP.f_c_UL, 0)
        RTS_PACKET.setRXpower(p_rx)
        RTS_PACKET.setdataRate(max_data_rate)
    


    def process_CTS_packet_ADAPT(self, CTS:CTS, currentSector):
        if(self.retransmissions > 0):
            self.retransmissions -= 1
        UL_PACKET = None
        arrival_time = CTS.timeStampTransmission + channel.compute_propagationDelay(self.distanceToAP) + CTS.transmissionDelay
        CTS.setupPropagationDelay(self.distanceToAP, self.ue_device.id)
        CTS.settimeStampArrival(arrival_time)

        for i in range(len(CTS.allocatedTimeSlots)):
            if CTS.allocatedUEID[i] == self.ue_device.id:
                find_time_slot = CTS.allocatedTimeSlots[i]
                data_rate_approved = CTS.allocateddataRate[i]
                if(find_time_slot < self.ue_device.UE_TRANSMISSIONS.check_earliest_transmission()):
                    print("Error MAC UE CTS Packet Processing -> Grant Received Prior To UE need for transmission\n")
                    sys.exit(1)
                linkType = constants.LoS
                UL_PACKET, NLoS_Signal = self.create_ULDATA_Packet(linkType,currentSector,find_time_slot,data_rate_approved)
        return UL_PACKET

    


