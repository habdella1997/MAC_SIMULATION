import os
import shutil
from datetime import datetime

def delete_old_folders():
    base_path = os.getcwd()
    # Define folders to check
    folders_to_check = ["Logs\PacketTrace", "Logs\\UE_LOG","Results"]
    
    for folder_name in folders_to_check:
        folder_path = os.path.join(base_path, folder_name)
        
        # Ensure the folder exists
        if not os.path.isdir(folder_path):
            print(f"{folder_name} does not exist at {base_path}")
            continue

        # List subfolders with datetime names
        subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        
        # Sort subfolders by datetime
        subfolders.sort(key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S"))
        
        # Delete all but the last 3 folders
        for folder in subfolders[:-3]:
            folder_to_delete = os.path.join(folder_path, folder)
            shutil.rmtree(folder_to_delete)
            print(f"Deleted {folder_to_delete}")
