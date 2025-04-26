
#TimeStampTransmission: Current Time Before transmission
#TimeStampArrival : current time + transmission delay + propagation delay.

import channel

class UL_GRANT:
    def __init__(self, timeSlot, dataRate):
        self.timeSlot = timeSlot
        self.dataRate = dataRate
        self.seqID = None
    def set_UL_sequenceID(self, seqID):
        self.seqID = seqID



class Packet:
    sequence_id = 0  # Class variable to keep track of sequence IDs
    
    CONTROL_PACKET_LENGTH = 0
    CONTROL_PACKET_RATE   = 0

    CONTROL_PACKET_RTS_RATE = 0

    DATA_PACKET_LENGTH = 0
    
    def __init__(self, linkDirection, sender, recipient, packetType, packetDEF):
        self.sender        = sender
        self.recipient     = recipient
        self.linkDirection = linkDirection
        self.sequence_id = Packet.sequence_id
        self.length = 0
        self.rate   = 0
        self.packetType = packetType
        self.packetDEF  = packetDEF
        if(packetType == "CNTRL"):
            self.length = Packet.CONTROL_PACKET_LENGTH
            self.rate   = Packet.CONTROL_PACKET_RATE
        else:
            self.length = Packet.DATA_PACKET_LENGTH
            self.rate   = None #determined at moment of transmission controlled by the MAC TOP
        Packet.sequence_id += 1  # Increment for next packet

class CTA(Packet):
    def __init__(self, sender, apSector):
        super().__init__("DOWNLINK", sender, '', "CNTRL","CTA")
        self.transmissionDelay     = 0
        self.propagationDelay      = []
        self.timeStampTransmission = 0
        self.timeStampArrival      = []
        self.timeStampArrival_UEID = []
        self.waitTime              = None
    def addRecepients(self, id):
        self.recipient = self.recipient + str(id) + ','
    def setupTransmissionDelay(self):
        self.transmissionDelay = channel.compute_transmissionTime(self.length, self.rate)
    def setupPropagationDelay(self, distance, ueID):
        propagationDelay = channel.compute_propagationDelay(distance)
        self.propagationDelay.append(propagationDelay)
        self.timeStampArrival_UEID.append(ueID)
    def settimeStampTransmission(self,currentTime):
        self.timeStampTransmission = currentTime
    def settimeStampArrival(self,time):
        self.timeStampArrival.append(time)
    def setupWaitTime(self, time):
        self.waitTime = time

class RTS(Packet):
    def __init__(self, sender, recepient,linkType):
        super().__init__("UPLINK",sender, recepient, "CNTRL","RTS")
        self.transmissionDelay = 0
        self.propagationDelay  = 0
        self.timeStampTransmission = 0
        self.timeStampArrival = 0 
        self.distanceToAP = 0
        self.computed_rxPower    = 0
        self.computed_data_rate  = 0 
        self.computed_modScheme  = 0 #AP will assigned modulation scheme depending on the MAC Algo
        self.UplinkTimeSlotDuration = 0
        self.linkType = linkType
        self.numberOfGrantsNeeded = 0
        self.bobo = []
        self.distance = 0
    def setupTransmissionDelay(self):
        self.transmissionDelay = channel.compute_transmissionTime(self.length, self.rate)
    def setupPropagationDelay(self, distance):
        self.propagationDelay = channel.compute_propagationDelay(distance)
        self.distance = distance
    def settimeStampTransmission(self,currentTime):
        self.timeStampTransmission = currentTime
    def settimeStampArrival(self):
        self.timeStampArrival = self.timeStampTransmission + self.transmissionDelay + self.propagationDelay 

    def setupLinkBudget(self,rxPower, dataRate, modScheme):
        self.computed_rxPower = rxPower
        self.computed_data_rate = dataRate
        self.computed_modScheme = modScheme
    def setupULDuration(self, rate):
        self.UplinkTimeSlotDuration = (Packet.DATA_PACKET_LENGTH / rate)

class CTS(Packet):
    def __init__(self, sender, apSector):
        super().__init__("DOWNLINK", sender, '', "CNTRL","CTS")
        self.transmissionDelay = 0
        self.propagationDelay  = []
        self.timeStampTransmission = 0
        self.timeStampArrival      = []
        self.timeStampArrival_UEID = []
        self.allocatedTimeSlots    = [] #Time Slots for UE Transmission
        self.allocatedUEID         = [] #UE IDs of which request to transmit has been accepted. ONLY ue's in this list can transmit... 
        self.allocateddataRate     = []
        self.ue_linkType           = []
    def setup_recepients(self):
        for id in self.allocatedUEID:
            self.recipient = self.recipient + str(id) + ','
    def setupTransmissionDelay(self):
        self.transmissionDelay = channel.compute_transmissionTime(self.length, self.rate)
    def setupPropagationDelay(self, distance,ueID):
        propagationDelay = channel.compute_propagationDelay(distance)
        self.propagationDelay.append(propagationDelay)
        self.timeStampArrival_UEID.append(ueID)
    def settimeStampTransmission(self,currentTime):
        self.timeStampTransmission = currentTime
    def settimeStampArrival(self,time):
        self.timeStampArrival.append(time)
    def setupTimeSlots(self,timeSlots, allocatedUE,dataRate,linkType_assigned):
        self.allocatedTimeSlots.append(timeSlots)
        self.allocatedUEID.append(allocatedUE)
        self.allocateddataRate.append(dataRate)
        self.ue_linkType.append(linkType_assigned)


class UL_DATA(Packet):
    def __init__(self, sender, recipient,linkType):
        super().__init__("UPLINK",sender,recipient, "DATA", "ULDATA")
        self.transmissionDelay = 0
        self.propagationDelay  = 0
        self.timeStampTransmission = 0
        self.timeStampArrival = 0 
        self.dataRate = 0
        self.distance = 0
        self.linkType = linkType
    def setupTransmissionDelay(self,rate):
        self.transmissionDelay = channel.compute_transmissionTime(self.length, rate)
        self.dataRate = rate
    def setupPropagationDelay(self, distance):
        self.propagationDelay = channel.compute_propagationDelay(distance)
        self.distance = distance
    def settimeStampTransmission(self,currentTime):
        self.timeStampTransmission = currentTime
    def settimeStampArrival(self):
        self.timeStampArrival = self.timeStampTransmission + self.transmissionDelay + self.propagationDelay
        
class ACK(Packet):
    def __init__(self, sender, apSector):
        super().__init__("DOWNLINK", sender, '', "CNTRL", "ACK")
        self.transmissionDelay = 0
        self.propagationDelay  = []
        self.timeStampTransmission = 0
        self.timeStampArrival      = []
        self.timeStampArrival_UEID = []
        self.packetsACKED_UELIST   = [] #list of UE devices that im ACKING <I think this is sequence id>
        self.ueIDlist      = [] 
        self.NLoS_data_rate = 0
        self.NLoS_distance  = 0
        self.NLoS_ULTransmissionTime = 0
    def setup_recepients(self,id):
        self.recipient = self.recipient + str(id) + ','
        self.ueIDlist.append(id)
    def setupTransmissionDelay(self):
        self.transmissionDelay = channel.compute_transmissionTime(self.length, self.rate)
    def setupPropagationDelay(self, distance,ueID):
        propagationDelay = channel.compute_propagationDelay(distance)
        self.propagationDelay.append(propagationDelay)
        self.timeStampArrival_UEID.append(ueID)
    def settimeStampTransmission(self,currentTime):
        self.timeStampTransmission = currentTime
    def settimeStampArrival(self,time):
        self.timeStampArrival.append(time)
    def setup_PacketAck(self,packetACK):
        self.packetsACKED_UELIST.append(packetACK)


    
    
