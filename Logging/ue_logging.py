import logging
import os
import csv
from datetime import datetime
from Objects import transmission2
from Objects import UE
from Objects import AP
class Logger:
    def __init__(self):
        logs_dir = "Logs/UE_LOG"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # Create a sub-folder based on the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sub_folder = os.path.join(logs_dir, timestamp)
        os.makedirs(sub_folder, exist_ok=True)
        self.topLevelFolder = sub_folder
    


        # self.xCor      = xCor
        # self.yCor      = yCor
        # self.AP        = None
        # self.id        = UE.UE_ID
        # self.UE_TRANSMISSIONS         = UETransmission(max_reTransmissions)
        # self.RFBox  = RFBox
        # UE.UE_ID = UE.UE_ID + 1
        # self.transmission_rate = transmission_rate
        # self.simEndTime        = endTime


    def write_UE_attr(self, ue_list):
        for ue in ue_list:
        # Construct the filename based on the UE id
            filename = os.path.join(self.topLevelFolder, f"UE_{ue.id}.txt")
            with open(filename, 'w') as file:
                # Write the header with UE id
                file.write(f"UE {ue.id} {{ ")
                
                # Retrieve all attributes and values as a dictionary
                attributes = vars(ue)
                
                thisdict = {
                "id_attribute"              : attributes['id'],
                "xCor"                      : attributes['xCor'],
                "yCor"                      : attributes['yCor'],
                
                "Logs_AppTransmissionTime"      : attributes['UE_TRANSMISSIONS'].Logs_AppTransmissionTime,
                "Logs_ActualTransmissionTime"   : attributes['UE_TRANSMISSIONS'].Logs_ActualTransmissionTime,
                "Logs_ULSeqID"                  : attributes['UE_TRANSMISSIONS'].Logs_ULSeqID,
                "Logs_AppSeqID"                 : attributes['UE_TRANSMISSIONS'].Logs_AppSeqID,
                "Logs_LinkType"                 : attributes['UE_TRANSMISSIONS'].Logs_LinkType,
                "Logs_NumTransmissions"         : attributes['UE_TRANSMISSIONS'].Logs_NumTransmissions,
                "Logs_Status"                   : attributes['UE_TRANSMISSIONS'].Logs_Status,
                "AP_Sector"                     : attributes['UE_TRANSMISSIONS'].Logs_APSector,

                "UE_Sector"                 : attributes['mySector'],
                "DistanceToAP"              : attributes['distanceToAP'],
                "PropagationDelay"          : attributes['propagationDelay']
                }
                
                # Format each attribute and value as 'attr_name = value' and join with commas
                attr_text = ', '.join([f"{attr} = {value}" for attr, value in thisdict.items()])
                
                # Write attributes inside the curly braces
                file.write(attr_text)
                
                # Close the curly braces
                file.write(" }\n")

  
