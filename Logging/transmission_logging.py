import logging
import os
import csv
from datetime import datetime
from Objects import transmission2
class Logger:
    def __init__(self):
        logs_dir = "Logs/PacketTrace"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # Create a sub-folder based on the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sub_folder = os.path.join(logs_dir, timestamp)
        os.makedirs(sub_folder, exist_ok=True)
        self.topLevelFolder = sub_folder
    
    def setup_msgTrace(self):
        logMSG = os.path.join(self.topLevelFolder,"actionLog.txt")
        self.logMSG = logMSG
        if not os.path.exists(logMSG):
            with open(logMSG, 'w') as file:
                pass  # Creates an empty file

    
    def setup_packetTrace(self):
        # Create CSV log file inside the sub-folder
        csv_file = os.path.join(self.topLevelFolder, "transmission_logs.csv")
        
        # Initialize CSV file with headers if it doesn't exist
        self.csv_file = csv_file
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Sequence_ID", "Direction","Sender", "Recipient", "Packet_Type",
                    "Transmission_Timestamp"
                ])
    
    def log_action(self, messages):
        with open(self.logMSG, 'a') as file:
            for message in messages:
                file.write(message)
                file.write("\n")

    def log_packet(self, packet):
        """Logs details of a Packet object to the CSV file."""
        if isinstance(packet, transmission2.Packet):
            # Common fields
            sequence_id = packet.sequence_id
            direction   = packet.linkDirection
            sender = packet.sender
            recipient = packet.recipient
            packet_type = packet.packetType
            transmission_timestamp = packet.timeStampTransmission

            # Arrival timestamps and UE IDs (for packets with multiple recipients)
            if hasattr(packet, 'timeStampArrival') and isinstance(packet.timeStampArrival, list):
                arrival_timestamps = ','.join(map(str, packet.timeStampArrival))
            else:
                arrival_timestamps = packet.timeStampArrival

            if hasattr(packet, 'timeStampArrival_UEID') and isinstance(packet.timeStampArrival_UEID, list):
                arrival_ueid = ','.join(map(str, packet.timeStampArrival_UEID))
            else:
                arrival_ueid = 'None'

            # Log into CSV
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    sequence_id, direction, sender, recipient, packet_type+"-"+packet.packetDEF,
                    transmission_timestamp
                ])

        else:
            raise ValueError("Invalid packet object passed to log_packet")

