from PIL import Image, ImageTk
import PIL
from tkinter import ttk
import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk
import re
import ast
import os 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle
import matplotlib.image as mpimg
import plotter
import io
import sys
import time
import platform

def fix_path(path):
    if platform.system() == "Windows":
        return path.replace("/", "\\")
    else:
        return path.replace("\\", "/")
    
def get_lastFolder(base_dir):
    base_path = os.path.abspath(os.path.join(os.path.dirname(base_dir), ".."))  
    base_path = fix_path(os.path.join(base_path,base_dir))     
    base_dir = base_path
    folders = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]
    sorted_folders = sorted(folders, reverse=True)
    if not sorted_folders:
        raise FileNotFoundError("No folders found in the specified base directory.")
    latest_folder = sorted_folders[0]
    return os.path.join(base_dir,latest_folder)


def load_latest_transmission_logs(base_dir,file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.abspath(os.path.join(script_dir, ".."))  
    base_path = os.path.join(base_path, base_dir)
    base_dir = base_path
    folders = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]
    sorted_folders = sorted(folders, reverse=True)
    if not sorted_folders:
        raise FileNotFoundError("No folders found in the specified base directory.")
    latest_folder = sorted_folders[0]
    latest_file_path = os.path.join(base_dir, latest_folder, file_name)
    if not os.path.isfile(latest_file_path):
        print(latest_file_path)
        raise FileNotFoundError(f"{file_name} not found in the latest folder: {latest_folder}")
    # Read and return the CSV file
    return latest_file_path

def get_ue_plot_paths(base_dir):
    plot_paths = []
    plot_labels = []
    base_path = os.path.abspath(os.path.join(os.path.dirname(base_dir), ".."))  
    base_path = fix_path(os.path.join(base_path,base_dir))     
    base_dir = base_path
    # Traverse through all the folders in 'Individual_UE_RESULTS'
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        # Check if it's a directory and the folder name is a number (i.e., UE_ID)
        if os.path.isdir(folder_path) and folder_name.isdigit():
            # Define possible plot files for each folder
            data_rate_path = os.path.join(folder_path, "Data Rate.png")
            latency_path = os.path.join(folder_path, "Latency.png")
            throughput_path = os.path.join(folder_path, "Throughput.png")
            
            # Check if the plot file exists and add to the lists with the corresponding labels
            if os.path.exists(data_rate_path):
                plot_paths.append(data_rate_path)
                plot_labels.append(f"UE_ID_{folder_name}:DataRate")
                
            if os.path.exists(latency_path):
                plot_paths.append(latency_path)
                plot_labels.append(f"UE_ID_{folder_name}:Latency")
                
            if os.path.exists(throughput_path):
                plot_paths.append(throughput_path)
                plot_labels.append(f"UE_ID_{folder_name}:Throughput")
    return plot_paths, plot_labels



# GUI Application
class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UNLAB THz Network Simulator")
        self.root.geometry("800x600")  # Set window size
        self.root.configure(bg=color_bg)   
        self.canvas = tk.Canvas(root,  highlightthickness=0.5)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1) 
        self.canvas.configure(bg=color_bg)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TMenubutton",
                            background=color_bg,
                            foreground=color_hover,
                            relief="flat")
        
        
        # UI Interface Variables. 
        self.lastUESelected = -1   
        self.ue_mappingCordinates = {}
        self.selected_timestamps = []
        self.ctrl_pressed = False  # Track if Ctrl key is pressed

        # Dividing canvas into two frames: Upper and Lower: Upper is for the Logs and Lowers for UE Activity. 
        top_frame    = tk.Frame(root, bg=color_bg, pady=10)
        bottom_frame = tk.Frame(root, bg=color_bg, pady=10)
        top_frame.pack(fill="x")
        bottom_frame.pack(fill="both", expand=True)

        ##########################################################################################################
        ##########################################################################################################
        # __________________________________________TOP FRAME LOGIC_____________________________________________##
        ##########################################################################################################
        ##########################################################################################################


        #####################################################################################################
        # Filter Frame <Logic for the Logs Filtering Option <Direction, Sender, Recepient, and Reset Button>#
        #####################################################################################################
        
        filter_frame = tk.Frame(top_frame, bg=color_bg) 
        filter_frame.pack(pady=10)
        filter_frame.configure()

        # Filter Frame Styling 
        label_style = {"font": ("Arial", 10, "bold"), "fg": color_fg, "bg": color_bg}
        style.configure("Dark.TCombobox", foreground=color_fg, background=color_field, fieldbackground=color_field, bordercolor=color_border, 
                        lightcolor=color_border, darkcolor=color_border, arrowcolor=color_fg, padding=4)
        style.map("Dark.TCombobox", fieldbackground=[("readonly", color_field), ("hover", color_hover)], 
                  background=[("active", color_hover)], arrowcolor=[("hover", color_fg)])
        
        # Dropdown for Direction
        tk.Label(filter_frame, text="Direction:", **label_style).pack(side=tk.LEFT, padx=5)
        self.direction_var = tk.StringVar()
        self.direction_menu = ttk.Combobox(filter_frame, textvariable=self.direction_var, values=directions,state="readonly",style="Dark.TCombobox" )
        self.direction_menu.pack(side=tk.LEFT)
        self.direction_menu.bind("<<ComboboxSelected>>", self.update_table)

        # Dropdown for Sender
        tk.Label(filter_frame, text="Sender:", **label_style).pack(side=tk.LEFT, padx=5)
        self.sender_var = tk.StringVar()
        self.sender_menu = ttk.Combobox(filter_frame, textvariable=self.sender_var, values=senders,state="readonly",style="Dark.TCombobox" )
        self.sender_menu.pack(side=tk.LEFT)
        self.sender_menu.bind("<<ComboboxSelected>>", self.update_table)

        # Dropdown for Recipient
        tk.Label(filter_frame, text="Recipient:", **label_style).pack(side=tk.LEFT, padx=5)
        self.recipient_var = tk.StringVar()
        self.recipient_menu = ttk.Combobox(filter_frame, textvariable=self.recipient_var, values=recipients,state="readonly",style="Dark.TCombobox" )
        self.recipient_menu.pack(side=tk.LEFT)
        self.recipient_menu.bind("<<ComboboxSelected>>", self.update_table)

        # Reset Button
        # ── NEW: button style to match theme ───────────────
        style.configure("Filter.TButton",background   = color_bg, foreground   = color_fg, font = ("Arial", 10, "bold"), borderwidth  = 0, padding = 6)
        style.map("Filter.TButton",background=[ ("active",  color_hover),  ("pressed",color_border)])
        reset_button = ttk.Button(filter_frame,text="Reset Filters",command=self.reset_filters,style="Filter.TButton")     # ← custom style name)
        reset_button.pack(side=tk.LEFT, padx=10)

        # Modify the Style of the dropdown window of the filter options <Need to manually overwrite the Tcombobox>
        root.option_add("*TCombobox*Listbox.background",         color_field)
        root.option_add("*TCombobox*Listbox.foreground",         color_fg)
        root.option_add("*TCombobox*Listbox.selectBackground",   color_accent)
        root.option_add("*TCombobox*Listbox.selectForeground",   color_fg)
        root.option_add("*TCombobox*Listbox.borderwidth",        0)

        #####################################################################################################
        # Table Frame <Logic for the Logs Table Display#
        #####################################################################################################

        style.configure("Dark.Treeview",background = color_field, foreground = color_fg,fieldbackground = color_field, bordercolor = color_border, rowheight = 22)
        style.map("Dark.Treeview",background=[("selected", color_selected)],foreground=[("selected", color_fg)])
        # header bar
        style.configure("Dark.Treeview.Heading",background = color_header, foreground = color_fg,bordercolor = color_border,relief = "flat")
        style.map("Dark.Treeview.Heading",background=[("active", color_hover)])

        # ────────────────── Scrollbars (vertical & horiz) ──────────
        style.configure("Vertical.TScrollbar",background   = color_hover,troughcolor  = color_bg,bordercolor  = color_border,arrowcolor   = color_fg,gripcount    = 0,relief       = "flat",)
        style.map("Vertical.TScrollbar",background=[("active", color_field)])

        style.configure("Horizontal.TScrollbar",background   = color_hover,troughcolor  = color_bg,bordercolor  = color_border,arrowcolor   = color_fg,gripcount    = 0,relief       = "flat",)
        style.map("Horizontal.TScrollbar",background=[("active", color_field)])



        # Frame for table and scrollbars
        table_frame = tk.Frame(top_frame, bg = color_bg)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(20, 0))  # Reduced bottom padding

        default_font = ("Arial", 10)
        self.root.option_add("*Font", default_font)

        # Vertical and horizontal scrollbars
        self.v_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        self.h_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Table to display logs
        columns = list(data.columns)
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings",style="Dark.Treeview", height=10,yscrollcommand=self.v_scroll.set,xscrollcommand=self.h_scroll.set)
        
        # Configure scrollbars
        self.v_scroll.config(command=self.table.yview)
        self.h_scroll.config(command=self.table.xview)

        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, stretch=True,anchor="center", width=100)

        self.table.bind("<Button-1>", self.on_column_click)
        self.table.pack(fill='both', expand=True, pady=10, padx = 10)
        self.update_table()

        # Add a double Click Action on the table --> Opens a new window with the packet info
        self.table.bind("<Double-1>", self.on_row_dbl_click)

        # Analysis Frame for Time Difference and additional visualizations
        analysis_frame = tk.Frame(top_frame)
        analysis_frame.pack(fill='both', expand=True, pady=(10, 5))
        analysis_frame.configure(bg=color_bg)

        self.time_diff_label = tk.Label(analysis_frame, text="Time Difference: ", font=("Arial", 13), anchor="e", fg=color_fg,bg=color_bg)
        self.time_diff_label.pack( padx=10, pady=5)
        
        root.bind("<Control_L>", self.ctrl_key_pressed)
        root.bind("<Control_R>", self.ctrl_key_pressed)
        root.bind("<KeyRelease-Control_L>", self.ctrl_key_released)
        root.bind("<KeyRelease-Control_R>", self.ctrl_key_released)

        
        
        ##########################################################################################################
        ##########################################################################################################
        # __________________________________________Bottom FRAME LOGIC_____________________________________________##
        ##########################################################################################################
        ##########################################################################################################


        #####################################################################################################
        # Transmissions Frame <Logic for the UE Trnamsission Attributes>
        #####################################################################################################


#         # Frame for the plot and UE ID table

        
        self.table_frame_new = tk.Frame(bottom_frame,width=100, bg=color_bg)
        self.table_frame_new.pack(side="left", fill="y", padx=5)  # Table takes up minimal width on the right

        self.centerFrame = tk.Frame(bottom_frame,width=300,padx=10, bg=color_bg)
        self.centerFrame.pack(side="left",fill='both',expand=True)
        
        self.rightFrame = tk.Frame(bottom_frame,width=300,bg=color_bg)
        self.rightFrame.pack(side="right",fill='both',expand=True)


        self.ue_id_frame = tk.Frame(self.table_frame_new, height=200, width=150)
        self.ue_id_frame.pack(side=tk.TOP, fill='both', expand=True)  # Expand to fill the width
        
        self.transmission_frame = tk.Frame(self.ue_id_frame,width=200,pady=10, bg=color_bg)
        self.transmission_frame.pack(side=tk.BOTTOM, fill='both', expand=True)  # Expand to fill the width
  
        self.transmission_table_data = ttk.Treeview(self.transmission_frame, columns=["(APP) Seq_Id", 
                                                                               "(APP) TX Time", 
                                                                               "(NW) TX Time", 
                                                                               "(NW) SEQ_Id" ,
                                                                               "Link Type",
                                                                               "Num ReTx",
                                                                               "Status",
                                                                               "AP Sector"], show="headings",height=10, style="Dark.Treeview")
       
        self.transmission_table_data.column(0,  stretch=0, width=112, anchor="center")
        self.transmission_table_data.column(1,  stretch=0, width=119,anchor="center")
        self.transmission_table_data.column(2,  stretch=0, width=119,anchor="center")
        self.transmission_table_data.column(3,  stretch=0, width=112,anchor="center")
        self.transmission_table_data.column(4,  stretch=0, width=112,anchor="center")
        self.transmission_table_data.column(5,  stretch=0, width=112,anchor="center")
        self.transmission_table_data.column(6,  stretch=0, width=60, anchor="center")
        self.transmission_table_data.column(6,  stretch=0, width=60, anchor="center")

        self.transmission_table_data.heading("(APP) Seq_Id", text="(APP) Seq_Id" , anchor="center")
        self.transmission_table_data.heading("(APP) TX Time", text="(APP) TX Time", anchor="center")
        self.transmission_table_data.heading("(NW) TX Time",     text="(NW) TX Time", anchor="center")
        self.transmission_table_data.heading("(NW) SEQ_Id",     text="(NW) SEQ_Id", anchor="center")

        self.transmission_table_data.heading("Link Type",     text="Link Type", anchor="center")
        self.transmission_table_data.heading("Num ReTx",     text="Num ReTx", anchor="center")
        self.transmission_table_data.heading("Status",     text="Status", anchor="center")
        self.transmission_table_data.heading("AP Sector",     text="AP Sector", anchor="center")
        self.transmission_table_data.bind("<Double-1>", self.on_transmission_row_double_click)

        
        # Sample UE IDs (replace with actual UE data from your DataFrame)
        self.ue_ids = senders
        self.ue_id_table = ttk.Treeview(self.ue_id_frame, columns=["UE ID", "Sector", "Distance To AP [m]", "Propagation Delay [s]"], show="headings", height=10, style="Dark.Treeview")
        self.ue_id_table.heading("UE ID", text="UE ID", anchor="center")
        self.ue_id_table.heading("Sector", text="Sector", anchor="center")
        self.ue_id_table.heading("Distance To AP [m]", text="Distance To AP [m]", anchor="center")
        self.ue_id_table.heading("Propagation Delay [s]", text="Propagation Delay [s]", anchor="center")

        # columns  →  
        self.ue_id_table.column("UE ID",                 anchor="center", width=80)
        self.ue_id_table.column("Sector",                anchor="center", width=80)
        self.ue_id_table.column("Distance To AP [m]",    anchor="center", width=140)
        self.ue_id_table.column("Propagation Delay [s]", anchor="center", width=160)

        for index,ue_id in enumerate(self.ue_ids):
            if(ue_id == 0 ):
                continue
            sector_path_ueid = load_latest_transmission_logs("Logs\\UE_LOG","UE_"+str(ue_id)+".txt")
            sector_num,dist,prop = self.extract_sector_from_file(sector_path_ueid, ue_id)
            self.ue_id_table.insert("", "end", values=(ue_id,sector_num,dist,prop) )
        
        self.ue_id_table.bind("<Double-1>", self.on_ue_id_click)

        self.ue_id_table.pack(fill='both', expand=True)
        self.transmission_table_data.pack(fill='both',expand=True)



    #####################################################################################################
    # Results Center Frame
    #####################################################################################################


        self.resultplot_frame = tk.Frame(self.centerFrame, width=400)  # Adjust width as needed
        self.resultplot_frame.configure(bg=color_bg)
        
        
        self.resultplot_frameTitle = tk.Label(self.centerFrame, text="Individual UE Results",
                                font=("Arial", 12, "bold"),
                                fg=color_fg,  bg=color_bg)
        self.resultplot_frameTitle.pack(side="top", pady=6)
        
        result_plotPaths = "Results\\"
        result_plotPaths = os.path.join(get_lastFolder(result_plotPaths), "Individual_UE_RESULTS")
        plot_paths, plot_labels = get_ue_plot_paths(result_plotPaths)
        plot_options = plot_labels

        dropdown = ttk.Combobox(self.centerFrame, values=plot_options, state="readonly",width=20, height=5, style="Dark.TCombobox")
        dropdown.set(plot_options[0])  # Set default option
        dropdown.pack(side="top", fill="x", pady=10)  
        self.resultplot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        dropdown.bind("<<ComboboxSelected>>", lambda event: self.plot_graph(dropdown.get(),plot_paths,plot_labels)) 
        # self.load_plot_image()

        # Display initial data

    ####################################################################################################
    #Right Frame Center Frame
    #################################################################################################### 

        self.mapGridTitle = tk.Label(self.rightFrame, text="Room Layout and UE Distribution",
                                font=("Arial", 12, "bold"),
                                fg=color_fg,  bg=color_bg)
        self.mapGridTitle.pack(side="top", pady=6)       
        # Load the PNG image file and add it to the plot frame
        path = load_latest_transmission_logs("Results",fix_path("Room\Room_Setup.png"))
        img = Image.open(path)  # Path to your saved image file
        #img_resized = img.resize((400, 400), PIL.Image.LANCZOS)  # Resize if needed
        img_resized = img.resize((300, 300), PIL.Image.LANCZOS)
        self.plot_image = ImageTk.PhotoImage(img_resized)
        
        # Add the image to the label to display in the plot frame
        plot_label = tk.Label(self.rightFrame, image=self.plot_image)
        plot_label.pack(fill='both', expand=True)
    

       
    # Function For the TOP FRAME to update the table once a filter is selected. 
    def update_table(self, event=None):
        for row in self.table.get_children():
            self.table.delete(row)

        # Apply filters in sequence
        filtered_data = data.copy()
        if self.direction_var.get():
            filtered_data = filtered_data[filtered_data['Direction'] == self.direction_var.get()]
            self.sender_menu['values'] = filtered_data['Sender'].unique().tolist()

        if self.sender_var.get():
            filtered_data = filtered_data[filtered_data['Sender'] == int(self.sender_var.get())]
            self.recipient_menu['values'] = filtered_data['Recipient'].unique().tolist()

        if self.recipient_var.get():
            filtered_data = filtered_data[filtered_data['Recipient'] == int(self.recipient_var.get())]

        for idx, row in filtered_data.iterrows():
            row_values = row.tolist()
            row_values[3] = str(row_values[3])
            if(row_values[3] == "nan"):
                row_values[3] = "NO UE in this sector"
            row_values[3] = row_values[3][:-1] if row_values[3].endswith(',') else row_values[3]
            background_color = color_field if row_values[1] == "DOWNLINK" else color_accent
            self.table.insert("", "end", values=row_values, tags=(idx,))
            self.table.tag_configure(idx, background=background_color)

    # Function For the TOP frame to reset the Log Table        
    def reset_filters(self):
        self.direction_var.set("")
        self.sender_var.set("")
        self.recipient_var.set("")
        self.sender_menu['values'] = senders
        self.recipient_menu['values'] = recipients
        self.update_table()
    
    # Function For Double Clicking on the Log Packet to open a new window. Finds the packet from the packetDump.pkl -> packet dictitionary
    # -> per sequence ID and populates table with the atteributes
    def on_row_dbl_click(self, event):
        item_id = self.table.identify_row(event.y)
        if not item_id:
            return

        # full tuple of column values for that row
        row_values = self.table.item(item_id, "values")

        # locate the Sequence‑ID column once
        seq_col_idx = self.table["columns"].index("Sequence_ID")  \
                    if "Sequence_ID" in self.table["columns"]   \
                    else 0          # fallback: first column

        packet_type_index = self.table["columns"].index("Packet_Type")  \
                    if "Packet_Type" in self.table["columns"]   \
                    else 0          # fallback: first column
        seq_id = row_values[seq_col_idx]
        packet_type = row_values[packet_type_index]
        pkt    = packet_by_id.get(int(seq_id))   # None if not found
        # ── build a pop‑up window ───────────────────────────
        pop = tk.Toplevel(self.root)
        pop.title(f"Packet {seq_id}")
        pop.configure(bg=color_bg)
        pop.geometry("550x520")                 # size, tweak as you like
        pop.resizable(True, True)

        # nice consistent font
        font_hdr = ("Arial", 11, "bold")
        # header label
        tk.Label(pop, text=f"Packet  #{seq_id}: {packet_type}", font=font_hdr,
                fg=color_fg, bg=color_bg).pack(pady=(20, 10))

         # Tree‑style attribute viewer
        tv = ttk.Treeview(pop, columns=("attr", "val"),
                        show="headings", height=12,
                        style="Dark.Treeview")
        tv.heading("attr", text="Attribute",anchor="center")
        tv.heading("val",  text="Value",anchor="center")
        tv.column("attr", anchor="center", width=140)
        tv.column("val",  anchor="center", width=220)
        tv.pack(fill="both", expand=True, padx=15, pady=10)
        # convert packet to dict & insert rows
        for k, v in vars(pkt).items():
            tv.insert("", "end", values=(k, v))
        ttk.Button(pop, text="Close", command=pop.destroy,style="Filter.TButton").pack(pady=(0, 15))
    
    
    ## Used for the Log Table to find the time difference between two selected packets. 
    def ctrl_key_pressed(self, event):
        self.ctrl_pressed = True

    def ctrl_key_released(self, event):
        self.ctrl_pressed = False
    
    # Function for the Log Table Frame, once a log is clicked it will get activated. Used to comapre timestamps.
    def on_column_click(self, event):
        # Identify the clicked row
        item_id = self.table.identify_row(event.y)
        if not item_id:
            return  # Click was outside of a row
        selected_timestamp = data['Transmission_Timestamp'][int(self.table.index(item_id))]  # Original timestamp
        self.selected_timestamps.append(selected_timestamp)

        if self.ctrl_pressed:
            if len(self.selected_timestamps) == 2:
                # Calculate time difference and update label
                time_diff = round(abs(self.selected_timestamps[1] - self.selected_timestamps[0]) , numeric_value_percision) 
                self.time_diff_label.config(text=f"Time Difference: {time_diff} [S]")
                self.selected_timestamps = []  # Reset for future calculations
            else:
                self.selected_timestamps = []
                self.time_diff_label.config(text=f"Time Difference: [S]")
        else:
            self.selected_timestamps = [selected_timestamp]
            self.time_diff_label.config(text=f"Time Difference: [S]")
            
    
    def extract_sector_from_file(self,file_path, target_id):
        if(target_id == 0):
            return 0
        with open(file_path, 'r') as file:
            # Read the file content
            file_content = file.read()

            # Find the line that contains the target ID
            id_line_pattern = f"id_attribute = {target_id}"
            if id_line_pattern in file_content:
                # Extract the sector number from the file content
                # We assume the sector is on the same line or close to the id_attribute line
                start_pos = file_content.find(id_line_pattern)
                sector_start_pos = file_content.find("UE_Sector")
                distpos = file_content.find("DistanceToAP")
                proppos = file_content.find("PropagationDelay")
                ue_Xcor = file_content.find("xCor")
                if sector_start_pos != -1 :
                    # Extract the sector number from the content after 'sector ='
                    sec_num = (file_content[file_content.find("UE_Sector"):].split('=')[1].split()[0]).replace(",","")
                    ue_Xcor = (file_content[file_content.find("xCor"):].split('=')[1].split()[0]).replace(",","")
                    self.ue_mappingCordinates[int(target_id)] = float(ue_Xcor)
                    distance = round(float( (file_content[file_content.find("DistanceToAP"):].split('=')[1].split()[0]).replace(",","")) ,3)
                    prop = (file_content[file_content.find("PropagationDelay"):].split('=')[1].split()[0]).replace(",","")
                    prop =  round(float(prop),numeric_value_percision)
                    return (sec_num,distance,prop)
        return None  # Return None if no match is found
    
    def on_ue_id_click(self, event):
        for row in self.transmission_table_data.get_children():
            self.transmission_table_data.delete(row)
        selected_item = self.ue_id_table.selection()
        ue_id_value = self.ue_id_table.item(selected_item[0])['values'][0]
        self.lastUESelected = ue_id_value
        file_path = load_latest_transmission_logs("Logs\\UE_LOG","UE_"+str(ue_id_value)+".txt")
        with open(file_path, 'r') as file:
            # Read the file content
            file_content = file.read()
            cleaned_content = re.sub(r'(\w+)\s*=', r'"\1":', file_content)
            ue_data = ast.literal_eval(cleaned_content[file_content.index('{'):]) 
            i1 = ue_data["Logs_AppSeqID"]
            i2 = ue_data["Logs_AppTransmissionTime"]
            i3 = ue_data["Logs_ActualTransmissionTime"]
            i4 = ue_data["Logs_ULSeqID"]
            i5 = ue_data["Logs_LinkType"]
            i6 = ue_data["Logs_NumTransmissions"]
            i7 = ue_data["Logs_Status"]
            i8 = ue_data["AP_Sector"]
            for v1,v2,v3,v4,v5,v6,v7,v8 in zip(i1,i2,i3,i4,i5,i6,i7,i8):
                    self.transmission_table_data.insert("", "end", values=(v1,v2,v3,v4,v5,v6,v7,v8 ))
    
    # Used to Plot the Individual UE Results
    def plot_graph(self,plot_type,paths,labels):
        for widget in self.resultplot_frame.winfo_children():
            widget.destroy()
        path_found = None
        for i,label in enumerate(labels):
            if(label == plot_type):
                path_found = paths[i]
 
        img = Image.open(path_found)  # Path to your saved image file
        img_resized = img.resize((400, 400), PIL.Image.LANCZOS)  # Resize if needed
        self.result_plot_image = ImageTk.PhotoImage(img_resized)
        
        # Add the image to the label to display in the plot frame
        plot_label = tk.Label(self.resultplot_frame, image=self.result_plot_image)
        plot_label.pack(fill='both', expand=True)
        
    # # Clear previous plot
    #     for widget in self.resultplot_frame.winfo_children():
    #         widget.destroy()

    #     # Example plot types
    #     if plot_type == "Plot 1":
    #         fig, ax = plt.subplots(figsize=(6, 4))
    #         ax.plot([1, 2, 3, 4], [1, 4, 9, 16], label="x^2")
    #         ax.set_title("Plot 1: x^2")
    #     elif plot_type == "Plot 2":
    #         fig, ax = plt.subplots(figsize=(6, 4))
    #         ax.plot([1, 2, 3, 4], [1, 2, 3, 4], label="x")
    #         ax.set_title("Plot 2: x")

    #     # Embed plot in the tkinter window
    #     canvas = FigureCanvasTkAgg(fig, master=self.resultplot_frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack()



    def on_transmission_row_double_click(self, event):
        selected_item = self.transmission_table_data.selection()
        if not selected_item:
            return  # No row selected

        # Get the value of the (APP) TX Time column for the selected row
        selected_row_data = self.transmission_table_data.item(selected_item)['values']
        app_tx_time = selected_row_data[2]  # Assuming "(APP) TX Time" is the second column
        linkType    = selected_row_data[4]
        
        # Open a new window to display the plot if NLoS Signal
        if(linkType == "LoS"):
            return
        
        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"Plot for (APP) TX Time: {app_tx_time} for UE: {self.lastUESelected}")
        plot_window.geometry("600x600")
        plot_window.configure(bg=color_bg)

        pickleFilePath = "Results\\"
        pickleFilePath = get_lastFolder(pickleFilePath) 
        pickleFilePath = os.path.join(pickleFilePath,"NLoSData","NLoSReflection.pkl")
        pickleFilePath = fix_path(pickleFilePath)

        NLoSDATA = []
        with open(pickleFilePath, 'rb') as file:  # Open the file in binary read mode
            NLoSDATA = pickle.load(file)

        ueID_NLoSData = NLoSDATA[self.lastUESelected]
        RFLoS_Signal = None
        for index,timeEntry in enumerate(ueID_NLoSData[0]):
            if(timeEntry==float(app_tx_time)):
                RFLoS_Signal = ueID_NLoSData[1][index]
       
        if(RFLoS_Signal==None):
            print("Error In Locating Transmission Instance. Exiting")
            sys.exit(-1)

        imageFilePath = "Results\\"
        base_result_folder =  get_lastFolder(imageFilePath)

        # Final absolute paths
        pickleFilePath_1 = os.path.join(base_result_folder, "Room", "mirrorFov", str(self.lastUESelected))
        pickleFilePath_2 = os.path.join(base_result_folder, "Room", "mirrorRoom", str(self.lastUESelected), "mirrorRoom.pkl")
        pickleFilePath_3 = os.path.join(base_result_folder, "Room", "NLoSAllSignals",  str(self.lastUESelected), "NLoSSignals.png")

        image_paths = [pickleFilePath_1, pickleFilePath_2, pickleFilePath_3]

        mirror_subfolders = [f for f in os.listdir(pickleFilePath_1) if os.path.isdir(os.path.join(pickleFilePath_1, f))]
        
        plot_window.img_cache = {}    # ⇠ attach a small dict to store images

        # Helper function to update the leftmost figure when dropdown changes
        def update_leftmost_image(selected_folder):
            pickleFilePath_1_new = os.path.join(get_lastFolder("Results\\"), "Room", "mirrorFoV",  str(self.lastUESelected)) 
            selected_path  = os.path.join(pickleFilePath_1_new, selected_folder, "mirrorRoom.png")
            if os.path.exists(selected_path):
                img = Image.open(selected_path).resize((500, 500), PIL.Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                # store photo so it isn’t garbage‑collected
                plot_window.img_cache["left"] = photo
                fov_img.configure(image=photo)           # swap image in place
                fov_title.configure(text=f"Field of View: {selected_folder}")


        selected_option = tk.StringVar(value="Select Mirror")
        dropdown = ttk.OptionMenu(plot_window, selected_option, "Select Mirror", *mirror_subfolders,
                                command=update_leftmost_image)
        dropdown.configure(style="Dark.TMenubutton")
        dropdown.pack(side=tk.TOP, fill=tk.X,
              padx=10,
              pady=(0, 100))   # 0 px above, 100 px below


        
        content = tk.Frame(plot_window, bg=color_bg)
        content.pack(fill="both", expand=True, padx=15, pady=15)
        for c in range(3):
            content.columnconfigure(c, weight=1)

        frames = []
        for col in range(3):
            f = tk.Frame(content, bg=color_bg, bd=1, relief="flat")
            f.grid(row=0, column=col, sticky="nsew", padx=6)   # 6‑px gap between panels
            frames.append(f)


        # ---------- frame‑0 widgets (title + image) ------------------
        fov_title = tk.Label(frames[0], text="Field of View",
                                font=("Arial", 12, "bold"),
                                fg=color_fg,  bg=color_bg)
        fov_title.pack(side="top", pady=6)
        fov_img  = tk.Label(frames[0], bg=color_bg)
        fov_img.pack(expand=True)

        NLoS_title = tk.Label(frames[1], text="NLoS Transmission Path",
                                font=("Arial", 12, "bold"),
                                fg=color_fg,  bg=color_bg)
        NLoS_title.pack(side="top", pady=6)
        
        nlos_img = tk.Label(frames[1], bg=color_bg)
        nlos_img.pack(expand=True)

        sectorData_title = tk.Label(frames[2], text="UE Transmission Stats",
                                font=("Arial", 12, "bold"),
                                fg=color_fg,  bg=color_bg)
        sectorData_title.pack(side="top", pady=6)
        
        secimg = tk.Label(frames[2], bg=color_bg)
        secimg.pack(expand=True)





        first_png = os.path.join(pickleFilePath_1, "mirror_0", "mirrorRoom.png")
        if os.path.exists(first_png):
            update_leftmost_image("mirror_0")
        
        with open(image_paths[1], "rb") as file:
            fig_new = pickle.load(file)
            ax = fig_new.gca()
            if(linkType == "NLoS"):
                plotter.plot_single_UE_links2(ax,RFLoS_Signal,self.ue_mappingCordinates[self.lastUESelected],0)
                plotter.plot_mirrors(plt,[RFLoS_Signal.mirror])
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img   = Image.open(buf).resize((500, 500), PIL.Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                # keep reference so Tk doesn’t GC it
                plot_window.img_cache["nlos"] = photo
                nlos_img.configure(image=photo)        # swap image in place


        with open(image_paths[2], "rb") as file:
            img   = Image.open(image_paths[2]).resize((500, 500), PIL.Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            # keep reference so Tk doesn’t GC it
            plot_window.img_cache["secimg"] = photo
            secimg.configure(image=photo)        # swap image in place
        


# ── Dark‑theme palette ────────────────────────────────────────────
color_bg        = "#5b2b2b"   # main background – charcoal
color_field     = "#3a3a3a"   # input/combobox field – slightly lighter
color_fg        = "#e0e0e0"   # text / icons – light gray
color_selected  = "#444c5c"   # row highlight – muted blue‑gray
color_accent    = "#007acc"   # accent blue (for buttons, etc.)
color_border   = "#505050"   # thin border
color_hover    = "#4a4a4a"   # field when mouse is over it
color_header    = "#454545"    # header bar bg

numeric_value_percision = 9

dataPath = load_latest_transmission_logs("Logs\\PacketTrace","transmission_logs.csv")
data = pd.read_csv(dataPath)
print("Reading logs from: " + dataPath)

packetPath = load_latest_transmission_logs("Logs\\PacketTrace", "packetDump.pkl")
packets = None
with open(packetPath, "rb") as f:
    packets = pickle.load(f)
packet_by_id = {p.sequence_id: p for p in packets}   # Dictionary Holding Packets with key being sequence ID

original_data = data
# Add formatted timestamp column in milliseconds (display only)
data['Transmission_Timestamp'] = (data['Transmission_Timestamp'] ).round(numeric_value_percision)  # Display in ms with 3 decimals

# Unique options for dropdown filters
directions = data['Direction'].unique().tolist()
senders = data['Sender'].unique().tolist()
senders.sort()
recipients = senders

# Initialize and run the application
root = tk.Tk()
app = LogViewerApp(root)
root.mainloop()
