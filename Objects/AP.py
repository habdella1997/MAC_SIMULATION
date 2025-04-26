import math
from tabulate import tabulate
import numpy as np
from Objects.Timer import Timer
import Objects.mirror as mirror
import RF

class AP:
    time_record   = []
    sector_record = []
    def __init__(self, RFBox, startingSector):
        self.id = 0
        
        self.RFBox = RFBox
        self.number_of_sectors = int(360 / RFBox.beamwidth)
        
        self.sector_map = []
        self.sector_leftBoundary  = [] # <x , y , beamwidth >
        self.sector_rightBoundary = [] 
        
        self.x = 0 #legacy
        self.y = 0 #legacy
        self.xCor = 0 
        self.yCor = 0

        self.startingSector = startingSector
        self.sectorTime     = 0
        self.currentSector  = 0 
    
    def setupAP(self):
        #TOP LeveL To setup AP Object and all its dependencies ...
        self.setup_sector_boundaries()
    
    def find_current_sector(self,sectorStartTime, currentSector, sectorTime, timeAdvance):
        totalSectors = self.number_of_sectors
        elapsedTime = timeAdvance - sectorStartTime

        # Calculate the number of sector transitions
        transitions = int(elapsedTime // sectorTime)

        # Calculate the new sector
        newSector = (currentSector + transitions) % totalSectors

        if(newSector == totalSectors):
            newSector = 0

        return newSector

    
    def get_currentSector(self, time):
        if(sectorTime > 0):
            number_of_sectors = self.number_of_sectors
            sectorTime        = self.sectorTime
            current_sector    = (math.floor(time / sectorTime) % number_of_sectors) + 1
            self.currentSector = int(current_sector)
            return int(current_sector)
        else:
            return self.currentSector #manually update the currentSector using the set_currentSector
        
    def set_currentSector(self,sector):
        self.currentSector = sector
    
    def setup_sector_boundaries(self):
        for i in range(1,int(self.number_of_sectors)+1):
            left_boundary  = (round(math.sin(math.radians(self.RFBox.beamwidth*(i-1))),7) , 
                              round(math.cos(math.radians(self.RFBox.beamwidth*(i-1))),7) , 
                              self.RFBox.beamwidth*(i-1) )
            
            right_boundary = (round(math.sin(math.radians(self.RFBox.beamwidth*(i))),7) ,
                              round(math.cos(math.radians(self.RFBox.beamwidth*(i))),7) ,
                              self.RFBox.beamwidth*(i))
            
            self.sector_leftBoundary.append(left_boundary)
            self.sector_rightBoundary.append(right_boundary)
            self.sector_map.append(i-1)
    
    def return_mySector(self, x,y):
        ueAngle = math.degrees(math.atan2(x,y))  #relative to the y axis
        if(ueAngle < 0):
            ueAngle += 360
        for i in range(0,self.number_of_sectors):
            left_boundary = self.sector_leftBoundary[i][2]
            right_boundary = self.sector_rightBoundary[i][2]
            if(ueAngle >= left_boundary and ueAngle < right_boundary):
                return self.sector_map[i]
            else:
                continue
        print("ERROR Fatal - UE is in no Sector")
        exit(-1)
        return
    




