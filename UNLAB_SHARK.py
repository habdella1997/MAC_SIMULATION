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

def get_lastFolder(base_dir):
    folders = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]
    sorted_folders = sorted(folders, reverse=True)
    if not sorted_folders:
        raise FileNotFoundError("No folders found in the specified base directory.")
    latest_folder = sorted_folders[0]
    return latest_folder


def load_latest_transmission_logs(base_dir,file_name):
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


dataPath = load_latest_transmission_logs("Logs\\PacketTrace","transmission_logs.csv")
data = pd.read_csv(dataPath)
print("Reading logs from: " + dataPath)

original_data = data
# Add formatted timestamp column in milliseconds (display only)
data['Transmission_Timestamp'] = (data['Transmission_Timestamp'] ).round(6)  # Display in ms with 3 decimals

# Unique options for dropdown filters
directions = data['Direction'].unique().tolist()
senders = data['Sender'].unique().tolist()
senders.sort()
recipients = senders

# GUI Application
class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HussamShark - Better Than WireShark")
        self.root.geometry("800x600")  # Set window size
        self.root.configure()   
        self.canvas = tk.Canvas(root,  highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1) 

        self.lastUESelected = -1   
        self.ue_mappingCordinates = {}
        # Variable to store selected items for time difference calculation
        self.selected_timestamps = []
        self.ctrl_pressed = False  # Track if Ctrl key is pressed
        
        # Filter Frame
        filter_frame = tk.Frame(root)
        filter_frame.pack(pady=10)
        filter_frame.configure()
        # Dropdown for Direction
        tk.Label(filter_frame, text="Direction:", bg="CadetBlue1").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar()
        self.direction_menu = ttk.Combobox(filter_frame, textvariable=self.direction_var, values=directions)
        self.direction_menu.pack(side=tk.LEFT)
        self.direction_menu.bind("<<ComboboxSelected>>", self.update_table)

        # Dropdown for Sender
        tk.Label(filter_frame, text="Sender:", bg="CadetBlue1").pack(side=tk.LEFT)
        self.sender_var = tk.StringVar()
        self.sender_menu = ttk.Combobox(filter_frame, textvariable=self.sender_var, values=senders)
        self.sender_menu.pack(side=tk.LEFT)
        self.sender_menu.bind("<<ComboboxSelected>>", self.update_table)

        # Dropdown for Recipient
        tk.Label(filter_frame, text="Recipient:", bg="CadetBlue1").pack(side=tk.LEFT)
        self.recipient_var = tk.StringVar()
        self.recipient_menu = ttk.Combobox(filter_frame, textvariable=self.recipient_var, values=recipients)
        self.recipient_menu.pack(side=tk.LEFT)
        self.recipient_menu.bind("<<ComboboxSelected>>", self.update_table)


        # Reset Button
        reset_button = tk.Button(filter_frame, text="Reset Filters",bg="CadetBlue3", command=self.reset_filters)
        reset_button.pack(side=tk.LEFT, padx=10)

        # Frame for table and scrollbars
        table_frame = tk.Frame(root)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(20, 0))  # Reduced bottom padding
        table_frame.configure()
        # table_frame.pack(fill='both', expand=True, pady=10)

        
        # Vertical and horizontal scrollbars
        self.v_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        self.h_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        

        # Table to display logs
        columns = list(data.columns)
        self.table = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=10,
            yscrollcommand=self.v_scroll.set
        )

 

         # Configure scrollbars
        self.v_scroll.config(command=self.table.yview)

        self.v_scroll.pack(side="right", fill="y")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, stretch=True, width=100)

        self.table.bind("<Button-1>", self.on_column_click)
        self.table.pack(fill='both', expand=True, pady=10)

        # Label for time difference display


        # Analysis Frame for Time Difference and additional visualizations
        analysis_frame = tk.Frame(root)
        analysis_frame.pack(fill='both', expand=True, pady=(10, 5))

        # analysis_frame = tk.Frame(root, height=100)
        # analysis_frame.pack(fill='both', expand=True, pady=(10,5))
        self.time_diff_label = tk.Label(analysis_frame, text="Time Difference: ", font=("Arial", 10), anchor="w")
        self.time_diff_label.pack(fill='x', padx=10, pady=5)
        
        root.bind("<Control_L>", self.ctrl_key_pressed)
        root.bind("<Control_R>", self.ctrl_key_pressed)
        root.bind("<KeyRelease-Control_L>", self.ctrl_key_released)
        root.bind("<KeyRelease-Control_R>", self.ctrl_key_released)

        # Frame for the plot and UE ID table

        
        
        
        self.table_frame_new = tk.Frame(analysis_frame,width=100)
        self.table_frame_new.pack(side="left", fill="y", padx=5)  # Table takes up minimal width on the right

        self.centerFrame = tk.Frame(analysis_frame,width=300,padx=10)
        self.centerFrame.pack(side="left",fill='both',expand=True)
        self.rightFrame = tk.Frame(analysis_frame,width=300)
        self.rightFrame.pack(side="right",fill='both',expand=True)

        self.ue_id_frame = tk.Frame(self.table_frame_new, height=200)
        self.ue_id_frame.pack(side=tk.TOP, fill='both', expand=True)  # Expand to fill the width
        self.transmission_frame = tk.Frame(self.ue_id_frame,width=200,pady=10)
        self.transmission_frame.pack(side=tk.BOTTOM, fill='both', expand=True)  # Expand to fill the width


        # self.plot_frame = tk.Frame(self.rightFrame, width=400)  # Adjust width as needed

        self.resultplot_frame = tk.Frame(self.centerFrame, width=400)  # Adjust width as needed
        
        
        self.rightFrame.pack(side="right", fill="both", expand=True)

        result_plotPaths = "Results\\"
        result_plotPaths += get_lastFolder(result_plotPaths) + "\\Individual_UE_RESULTS"
        plot_paths, plot_labels = get_ue_plot_paths(result_plotPaths)
        plot_options = plot_labels
        dropdown = ttk.Combobox(self.centerFrame, values=plot_options, state="readonly",width=20, height=5)
        dropdown.set(plot_options[0])  # Set default option
        dropdown.pack(side="top", fill="x", pady=10)  
        self.resultplot_frame.pack(fill="both", expand=True)
        # Bind dropdown selection to update plot
        dropdown.bind("<<ComboboxSelected>>", lambda event: self.plot_graph(dropdown.get(),plot_paths,plot_labels))
        
        
        # self.table_frame_transmission = tk.Frame(analysis_frame)
        # self.table_frame_transmission.pack(side="left", fill="y", padx=20)  # Table takes up minimal width on the right
        

      
   
        self.transmission_data = []
	
        self.transmission_table_data = ttk.Treeview(self.transmission_frame, columns=["(APP) Seq_Id", 
                                                                               "(APP) TX Time", 
                                                                               "(NW) TX Time", 
                                                                               "(NW) SEQ_Id" ,
                                                                               "Link Type",
                                                                               "Num ReTx",
                                                                               "Status",
                                                                               "AP Sector"], show="headings",height=10)
       
        self.transmission_table_data.column(0, anchor="w", stretch=0, width=112)
        self.transmission_table_data.column(1, anchor="w", stretch=0, width=119)
        self.transmission_table_data.column(2, anchor="w", stretch=0, width=119)
        self.transmission_table_data.column(3, anchor="w", stretch=0, width=112)
        self.transmission_table_data.column(4, anchor="w", stretch=0, width=112)
        self.transmission_table_data.column(5, anchor="w", stretch=0, width=112)
        self.transmission_table_data.column(6, anchor="w", stretch=0, width=60)
        self.transmission_table_data.column(6, anchor="w", stretch=0, width=60)

        self.transmission_table_data.heading("(APP) Seq_Id", text="(APP) Seq_Id")
        self.transmission_table_data.heading("(APP) TX Time", text="(APP) TX Time")
        self.transmission_table_data.heading("(NW) TX Time",     text="(NW) TX Time")
        self.transmission_table_data.heading("(NW) SEQ_Id",     text="(NW) SEQ_Id")

        self.transmission_table_data.heading("Link Type",     text="Link Type")
        self.transmission_table_data.heading("Num ReTx",     text="Num ReTx")
        self.transmission_table_data.heading("Status",     text="Status")
        self.transmission_table_data.heading("AP Sector",     text="AP Sector")
        self.transmission_table_data.bind("<Double-1>", self.on_transmission_row_double_click)

        
        # Sample UE IDs (replace with actual UE data from your DataFrame)
        self.ue_ids = senders
        self.ue_id_table = ttk.Treeview(self.ue_id_frame, columns=["UE ID", "Sector", "Distance To AP [m]", "Propagation Delay [ns]"], show="headings", height=10)
        self.ue_id_table.heading("UE ID", text="UE ID")
        self.ue_id_table.heading("Sector", text="Sector")
        self.ue_id_table.heading("Distance To AP [m]", text="Distance To AP [m]")
        self.ue_id_table.heading("Propagation Delay [ns]", text="Propagation Delay [ns]")
        sector_path = "Logs\\UE_LOG\\2024-11-08_14-51-01\\UE_"
        # Populate UE ID table and bind click event
        for index,ue_id in enumerate(self.ue_ids):
            if(ue_id == 0 ):
                continue
            sector_path_ueid = load_latest_transmission_logs("Logs\\UE_LOG","UE_"+str(ue_id)+".txt")
            sector_num,dist,prop = self.extract_sector_from_file(sector_path_ueid, ue_id)
            self.ue_id_table.insert("", "end", values=(ue_id,sector_num,dist,prop))
        self.ue_id_table.bind("<Double-1>", self.on_ue_id_click)
        self.ue_id_table.pack(fill='both', expand=True)
        self.transmission_table_data.pack(fill='both',expand=True)
        
        self.load_plot_image()

        # Display initial data
        self.update_table()
    
    def load_plot_image(self):
        # Load the PNG image file and add it to the plot frame
        path = load_latest_transmission_logs("Results","Room\\Room_Setup.png")
        print("Image Path: " + path)
        img = Image.open(path)  # Path to your saved image file
        img_resized = img.resize((400, 400), PIL.Image.LANCZOS)  # Resize if needed
        self.plot_image = ImageTk.PhotoImage(img_resized)
        
        # Add the image to the label to display in the plot frame
        plot_label = tk.Label(self.rightFrame, image=self.plot_image)
        plot_label.pack(fill='both', expand=True)
    
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

            # latencies = []
            # for app, ack in zip(app_times, ack_times):
            #     latencies.append(str(round((ack-app)*(1**6) , 6)))
            # print(latencies)
            for v1,v2,v3,v4,v5,v6,v7,v8 in zip(i1,i2,i3,i4,i5,i6,i7,i8):
                    #latency = round((ack-app)* (10**3),6)
                    self.transmission_table_data.insert("", "end", values=(v1,v2,v3,v4,v5,v6,v7,v8 ))
       

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
            background_color = "CadetBlue2" if row_values[1] == "DOWNLINK" else "CadetBlue3"
            self.table.insert("", "end", values=row_values, tags=(idx,))
            self.table.tag_configure(idx, background=background_color)
        
    
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
                    prop =  round(float(prop)* (10**6),6)
                    return (sec_num,distance,prop)
        return None  # Return None if no match is found

    def reset_filters(self):
        self.direction_var.set("")
        self.sender_var.set("")
        self.recipient_var.set("")
        self.sender_menu['values'] = senders
        self.recipient_menu['values'] = recipients
        self.update_table()

    def ctrl_key_pressed(self, event):
        self.ctrl_pressed = True

    def ctrl_key_released(self, event):
        self.ctrl_pressed = False

    def on_column_click(self, event):
        # Identify the clicked row
        item_id = self.table.identify_row(event.y)
        if not item_id:
            return  # Click was outside of a row


        selected_timestamp = data['Transmission_Timestamp'][int(self.table.index(item_id))]  # Original timestamp
        self.selected_timestamps.append(selected_timestamp)

        if self.ctrl_pressed:
            print(((self.selected_timestamps)))
            if len(self.selected_timestamps) == 2:
                # Calculate time difference and update label
                time_diff = round(abs(self.selected_timestamps[1] - self.selected_timestamps[0]) , 6) 
                self.time_diff_label.config(text=f"Time Difference: {time_diff} [mS]")
                self.selected_timestamps = []  # Reset for future calculations
            else:
                self.selected_timestamps = []
                self.time_diff_label.config(text=f"Time Difference: [mS]")
        else:
            self.selected_timestamps = [selected_timestamp]
            self.time_diff_label.config(text=f"Time Difference: [mS]")
    
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
        # Identify the clicked row
        selected_item = self.transmission_table_data.selection()
        if not selected_item:
            return  # No row selected

        # Get the value of the (APP) TX Time column for the selected row
        selected_row_data = self.transmission_table_data.item(selected_item)['values']
        app_tx_time = selected_row_data[2]  # Assuming "(APP) TX Time" is the second column
        linkType    = selected_row_data[4]
        # Open a new window to display the plot
        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"Plot for (APP) TX Time: {app_tx_time}")
        plot_window.geometry("600x400")

        pickleFilePath = "Results\\"
        pickleFilePath += get_lastFolder(pickleFilePath) + "\\NLoSData\\NLoSReflection.pkl"

        NLoSDATA = []
        with open(pickleFilePath, 'rb') as file:  # Open the file in binary read mode
            NLoSDATA = pickle.load(file)

        ueID_NLoSData = NLoSDATA[self.lastUESelected]
        RFLoS_Signal = None
        for index,timeEntry in enumerate(ueID_NLoSData[0]):
            if(timeEntry==float(app_tx_time)):
                RFLoS_Signal = ueID_NLoSData[1][index]
                print("Found")
        
        print("reflect slope: " + str(RFLoS_Signal.reflect_slope))
        print("reflect x : " + str(RFLoS_Signal.reflect_x))
        print("reflect y : " + str(RFLoS_Signal.reflect_y))
        fig, axes = plt.subplots(1, 3, figsize=(16, 3))  # 4 plots side by side
        titles = [
            "Image 1",
            "Image 2",
            "Image 3"
                            ]
        imageFilePath = "Results\\"
        pickleFilePath_1 = imageFilePath+get_lastFolder(imageFilePath) + "\\Room\\mirrorFoV\\" + str(self.lastUESelected) 
        pickleFilePath_2 = imageFilePath+get_lastFolder(imageFilePath) + "\\Room\\mirrorRoom\\" + str(self.lastUESelected) +"\\mirrorRoom.pkl"
        pickleFilePath_3 = imageFilePath+get_lastFolder(imageFilePath) + "\\Room\\NLoSAllSignals\\" + str(self.lastUESelected) + "\\NLoSSignals.png"
        image_paths = [pickleFilePath_1,pickleFilePath_2,pickleFilePath_3]

        mirror_subfolders = [f for f in os.listdir(pickleFilePath_1) if os.path.isdir(os.path.join(pickleFilePath_1, f))]
        
        # Helper function to update the leftmost figure when dropdown changes
        def update_leftmost_image(selected_folder):
            pickleFilePath_1_new = imageFilePath+get_lastFolder(imageFilePath) + "\\Room\\mirrorFoV\\" + str(self.lastUESelected) 
            selected_path  = os.path.join(pickleFilePath_1_new, selected_folder, "mirrorRoom.png")
            if os.path.exists(selected_path):
                img = mpimg.imread(selected_path)
                axes[0].imshow(img)
                axes[0].set_title(f"Field of View of Mirror: {selected_folder.replace('_', ' ')}")
                axes[0].axis("off")
                canvas.draw()

         # Dropdown menu for selecting mirror subfolders
        selected_option = tk.StringVar(value="Select Mirror")
        dropdown = ttk.OptionMenu(plot_window, selected_option, None, *mirror_subfolders,
                                command=update_leftmost_image)
        dropdown.pack(side=tk.TOP, fill=tk.X)

        initial_image  = os.path.join(pickleFilePath_1, "mirror_0", "mirrorRoom.png")  # Default image path
        initial_image3 = os.path.join(pickleFilePath_3, "mirror_0", "NLoSSignals.png")  # Default image path
        
        if os.path.exists(initial_image):
            img = mpimg.imread(initial_image)
            axes[0].imshow(img)
            axes[0].set_title("Field of View of Mirror: 0")
            axes[0].axis("off")
        else:
            axes[0].text(0.5, 0.5, "Image not found", fontsize=12, ha="center")
            axes[0].set_title("Mirror Room")
            axes[0].axis("off")
        


        for i, path in enumerate(image_paths):
            if(i==0 ):
                continue
            try:
                if(i==1):
                    with open(path, "rb") as file:
                        fig_new = pickle.load(file)
                        ax = fig_new.gca()
                        if(linkType == "NLoS"):
                            plotter.plot_single_UE_links2(ax,RFLoS_Signal,self.ue_mappingCordinates[self.lastUESelected],0)
                            plotter.plot_mirrors(plt,[RFLoS_Signal.mirror])
                            print("heree" + str(self.ue_mappingCordinates[self.lastUESelected]))
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            buf.seek(0)
                            # Convert the buffer to an image
                            img = Image.open(buf)
                            axes[i].imshow(img)
                            axes[i].set_title("Actual NLoS Signal Transmission")
                            axes[i].axis("off")  # Hide axes for the plot as an image
                        else:

                            print("Nonon")
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            buf.seek(0)
                            # Convert the buffer to an image
                            img = Image.open(buf)
                            axes[i].imshow(img)
                            axes[i].set_title(titles[i])
                            axes[i].axis("off")  # Hide axes for the plot as an image

                else:
                    img = mpimg.imread(path)
                    axes[i].imshow(img)
                    axes[i].set_title("All Possible NLoS Signal Transmissions")
                    axes[i].axis("off")  # Hide axes for images
                    print(path)
            except FileNotFoundError:
                axes[i].text(0.5, 0.5, "Image not found", fontsize=12, ha="center")
                axes[i].set_title(titles[i])
                axes[i].axis("off")
        
        fig.tight_layout(pad=3)
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)





        # Generate a simple plot (example: sine wave using (APP) TX Time as frequency)
        # fig, ax = plt.subplots(figsize=(6, 4))
        # time = [i * 0.1 for i in range(100)]
        # sine_wave = [app_tx_time * (0.5 + 0.5 * (-1) ** int(i / 10)) for i in range(100)] # Example wave function
        # ax.plot(time, sine_wave)
        # ax.set_title(f"Sine Wave for (APP) TX Time: {app_tx_time}")
        # ax.set_xlabel("Time")
        # ax.set_ylabel("Amplitude")
        # ax.grid(True)

        # Embed the plot into the new window
        # canvas = FigureCanvasTkAgg(fig, master=plot_window)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill="both", expand=True)




# Initialize and run the application
root = tk.Tk()
app = LogViewerApp(root)
root.mainloop()
