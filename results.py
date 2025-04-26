import logging
import os
import csv
from datetime import datetime
from Objects import transmission2
from collections import defaultdict
import plotter
import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
class Results_Data:
    def __init__(self,numSectors):
        self.results_latency  = []
        self.results_datarate = []
        self.results_ueid     = []
        self.RTS_Collisions   = []
        self.RTS_SuccessRate  = []
        self.RTS_Total_Transmissions = []
        self.sector_activity_RTS     = {x: [] for x in range(0,numSectors)}
        self.sector_activity_UL      = {x: [] for x in range(0,numSectors)}
    def add_results(self, latency,data_rate,ueid):
        self.results_latency.append(latency)
        self.results_datarate.append(data_rate)
        self.results_ueid.append(ueid)
    def add_collision_RTS(self, numberOfCollisions, numberOfPackets):
        self.RTS_Collisions.append(numberOfCollisions)
        self.RTS_Total_Transmissions.append(numberOfPackets)
        if(numberOfPackets>0):
            self.RTS_SuccessRate.append((1 - (numberOfCollisions/numberOfPackets))*100)
        else:
            if(numberOfCollisions>0):
                print("Collisions occured w/o any packets")
                sys.exit(1)
    def add_sector_activity_RTS(self, sector,activity):
        self.sector_activity_RTS[sector].append(activity)
    def add_sector_activity_UL(self, sector,activity):
        self.sector_activity_UL[sector].append(activity)

class Results:
    def __init__(self):
        logs_dir = "Results"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # Create a sub-folder based on the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sub_folder = os.path.join(logs_dir, timestamp)
        os.makedirs(sub_folder, exist_ok=True)
        self.topLevelFolder = sub_folder
    
    def setup_NLoSReflectionLog(self, dictionaryData):
        sub_sub_folder = os.path.join(self.topLevelFolder, "NLoSData")
        os.makedirs(sub_sub_folder, exist_ok=True)
        file_path = os.path.join(sub_sub_folder,"NLoSReflection.pkl")
        with open(file_path, "wb") as pickle_file:
            pickle.dump(dictionaryData, pickle_file)
    
    def setup_ue_perf(self, ue_id, plotName, data, xlabel, ylabel, title, legend_label):
        sub_sub_folder = os.path.join(self.topLevelFolder, "Individual_UE_RESULTS")
        os.makedirs(sub_sub_folder, exist_ok=True)
        sub_sub_sub_folder = os.path.join(sub_sub_folder, str(ue_id))
        os.makedirs(sub_sub_sub_folder, exist_ok=True)
        np.savetxt(sub_sub_sub_folder + "\\data.txt", data, fmt='%d',)  # Change fmt for desired precision
        # Full path for saving the plot
        file_path = os.path.join(sub_sub_sub_folder, plotName)
        plotter.results_create_line_plot(None, data, xlabel, ylabel, title, legend_label, file_path)
        



    def setup_avg_perf(self, plotName):
        sub_sub_folder = os.path.join(self.topLevelFolder, str("AVERAGE"))
        os.makedirs(sub_sub_folder, exist_ok=True)
        # Full path for saving the plot
        return os.path.join(sub_sub_folder, plotName)
    
    
    def save_room(self, plot):
        sub_sub_folder = os.path.join(self.topLevelFolder, str("Room"))
        os.makedirs(sub_sub_folder, exist_ok=True)
        # Full path for saving the plot
        file_path = os.path.join(sub_sub_folder, "Room_Setup")
        plot.savefig(file_path)
        plot.close()
    
    def save_mirrorRoom(self, plot, ueid):
        sub_sub_folder = os.path.join(self.topLevelFolder, str("Room"))
        os.makedirs(sub_sub_folder, exist_ok=True)
        sub_sub_sub_folder = os.path.join(sub_sub_folder, str("mirrorRoom\\"+str(ueid)))
        os.makedirs(sub_sub_sub_folder, exist_ok=True)
        # Full path for saving the plot
        file_path = os.path.join(sub_sub_sub_folder, "mirrorRoom.pkl")
        # plot.savefig(file_path)
        # plot.close()
        fig = plot.gcf()  # Get the current figure
        with open(file_path, "wb") as file:
            pickle.dump(fig,file)
    
    def save_mirrorFoV(self,plot,ueid,mirror_index):
        sub_sub_folder = os.path.join(self.topLevelFolder, str("Room"))
        os.makedirs(sub_sub_folder, exist_ok=True)
        sub_sub_sub_folder = os.path.join(sub_sub_folder, str("mirrorFoV\\"+str(ueid)))
        os.makedirs(sub_sub_sub_folder, exist_ok=True)
        sub_sub_sub_sub_folder = os.path.join(sub_sub_sub_folder, "mirror_"+(mirror_index))
        os.makedirs(sub_sub_sub_sub_folder, exist_ok=True)
        # Full path for saving the plot
        file_path = os.path.join(sub_sub_sub_sub_folder, "mirrorRoom")
        plot.savefig(file_path)
        plot.close()
    

    def save_AllNLoSSingals(self, plot, ueid,indexer):
        sub_sub_folder = os.path.join(self.topLevelFolder, str("Room"))
        os.makedirs(sub_sub_folder, exist_ok=True)
        sub_sub_sub_folder = os.path.join(sub_sub_folder, str("NLoSAllSignals\\"+str(ueid)))
        os.makedirs(sub_sub_sub_folder, exist_ok=True)
        # Full path for saving the plot
        file_path = os.path.join(sub_sub_sub_folder, "NLoSSignals")
        plot.savefig(file_path)
        plot.close()
    
    def savegeneralplot(self,plot,name):
        file_path = os.path.join(self.topLevelFolder, name)
        plot.savefig(file_path, dpi=300,bbox_inches='tight' )

    #Saves the latency, data_rate, and throughput of different users in a simulation

    def process_results_generic(self, macResults, PAYLOADSIZE,showPlots=False, savePlots=True):
        user_ids = macResults.results_ueid       
        latencies = macResults.results_latency 
        data_rates = macResults.results_datarate 
        
        # Step 1: Group values by user_id
        grouped_data = defaultdict(lambda: {'latencies': [], 'data_rates': []})
        for uid, latency, data_rate in zip(user_ids, latencies, data_rates):
            grouped_data[uid]['latencies'].append(latency)
            grouped_data[uid]['data_rates'].append(data_rate)
        
        # for uid, data in grouped_data.items():
        #     user_latencies = np.array(data['latencies'])
        #     user_data_rates = np.array(data['data_rates'])
        #     user_throughput = PAYLOADSIZE / user_latencies
        #     self.setup_ue_perf(uid,"Latency", user_latencies*(1e3), 'Measurement Index', 'Latency (ms)', f"Latencies for User {uid}", f"User {uid} Latency")
        #     self.setup_ue_perf(uid, "Data Rate",user_data_rates/(1e9), 'Measurement Index', 'Data Rate (Gbps)',f"Data Rates for User {uid}", f"User {uid} Data Rate")
        #     self.setup_ue_perf(uid, "Throughput",user_throughput/(1e9), 'Measurement Index', 'Throughput (Gbps)',f"Throughput for User {uid}", f"User {uid} Throughput")
                
            

        # Step 3: Calculate averages and create histograms for all users
        avg_latencies = []
        avg_data_rates = []
        avg_throughputs = []
        avg_throughput_across_all = []
        uid_list = []
        for uid, data in grouped_data.items():
            uid_list.append(uid)
            avg_latencies.append(np.mean(data['latencies']) * (1e3))
            avg_data_rates.append(np.mean(data['data_rates']) / (1e9))
            avg_throughputs.append( np.mean(PAYLOADSIZE / np.array(data['latencies'])) / (1e9))
            avg_throughput_across_all = avg_throughput_across_all + (PAYLOADSIZE / np.array(data['latencies'])).tolist()
        
        avg_throughput_across_all_val = np.mean(avg_throughput_across_all) / (1e9)

        # # Histogram of average latencies
        # latency_file_path = self.setup_avg_perf("Latency")
        # data_file_path    = self.setup_avg_perf("Data Rate")
        # thruput_file_path = self.setup_avg_perf("Throughput")
        
        # avg_latency_hist    = plotter.results_create_histogram_plot(uid_list, avg_latencies, 'Measurement Index','Average Latency (ms)','Histogram of Average Latency Across All Users',latency_file_path)
        # avg_data_rate_hist  = plotter.results_create_histogram_plot(uid_list, avg_data_rates, 'Measurement Index','Average Data Rate (Gbps)', 'Histogram of Average Data Rate Across All Users',data_file_path)
        # avg_throughput_hist = plotter.results_create_histogram_plot(uid_list, avg_throughputs, 'Measurement Index', 'Average Throughput (Gbps)','Histogram of Average Throughput Across All Users',thruput_file_path)
        
        return avg_throughput_across_all_val