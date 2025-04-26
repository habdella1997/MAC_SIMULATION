import tkinter as tk
from tkinter import ttk
import pandas as pd

class gui_top:
    GUI_NAME = "THz LOG TRACE: MAC LEVEL LOG"
    
    def __init__(self):
        self.root - tk.Tk()
        self.root.title(gui_top.GUI_NAME)
        self.root.geometry("800x600")
    
    
    def log_setup(self, file, ueIDList, APID):
        data = pd.read_csv(file)
        self.data_file = data
        self.data_file['Transmission_Timestamp'] = (data['Transmission_Timestamp']*1000).round(6)
        directions = ["DOWNLINK" , "UPLINK"]
        senders = APID + ueIDList
        receivers = senders
        self.filter_directions = directions
        self.filter_senders    = senders 
        self.filter_receivers  = receivers
    

    def setup_GUI(self):
        #TOP FRAME -> FILTER 
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        #DROP DOWN OPTIONS:
        tk.Label(filter_frame, text="Direction: ").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar()
        self.direction_menu = ttk.Combobox(filter_frame,textvariable=self.direction_var, values=self.filter_directions)
        self.direction_menu.pack(side=tk.LEFT)
        self.direction_menu.bind("<<ComboboxSelected>>",self.update_table)

        tk.Label(filter_frame, text="Sender: ").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar()
        self.direction_menu = ttk.Combobox(filter_frame,textvariable=self.direction_var, values=self.filter_senders)
        self.direction_menu.pack(side=tk.LEFT)
        self.direction_menu.bind("<<ComboboxSelected>>",self.update_table)

        tk.Label(filter_frame, text="Recipient: ").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar()
        self.direction_menu = ttk.Combobox(filter_frame,textvariable=self.direction_var, values=self.filter_receivers)
        self.direction_menu.pack(side=tk.LEFT)
        self.direction_menu.bind("<<ComboboxSelected>>",self.update_table)

        #reset Button
        reset_button = tk.Button(filter_frame, text="Reset Filter", command=self.reset_filters)
        reset_button.pack(side=tk.LEFT, padx=20)

        #Middle Frame -> Logs
        table_frame = tk.Frame(self.root)
        table_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.7)  # 70% of the height

