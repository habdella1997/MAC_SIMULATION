import os
import shutil
from datetime import datetime

def delete_old_folders(keep_last_n=0):
    # Automatically resolve root directory whether on Mac or Windows
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))        
    # Define relative folders to check
    folders_to_check = [
        os.path.join("Logs", "PacketTrace"),
        os.path.join("Logs", "UE_LOG"),
        "Results"
    ]

    for folder_name in folders_to_check:
        folder_path = os.path.join(base_path, folder_name)

        if not os.path.isdir(folder_path):
            print(f"⚠️  Folder does not exist: {folder_path}")
            continue
        


        # Get all subfolders with valid datetime names
        subfolders = [
            f for f in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, f))
        ]

        try:
            subfolders.sort(
                key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S")
            )
        except ValueError:
            print(f"⚠️  Skipped sorting {folder_path} due to invalid folder name format.")
            continue
        
        folders_to_delete = None
        if keep_last_n == 0:
            folders_to_delete = subfolders  # delete everything
        else:
            folders_to_delete = subfolders[:-keep_last_n]

        for folder in folders_to_delete:
            folder_to_delete_path = os.path.join(folder_path, folder)
            try:
                shutil.rmtree(folder_to_delete_path)
                #print(f"✅ Deleted: {folder_to_delete_path}")
            except Exception as e:
                print(f"❌ Failed to delete {folder_to_delete_path}: {e}")
