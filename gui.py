import os
import shutil
from tkinter import Tk, Label, Button, filedialog
from phi_removal import remove_phi

class DicomProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("DICOM Processor")

        self.label = Label(master, text="Select DICOM Root Folder:")
        self.label.pack()

        self.select_button = Button(master, text="Select Folder", command=self.select_folder)
        self.select_button.pack()

        self.process_button = Button(master, text="Process DICOM Files", command=self.process_dicom)
        self.process_button.pack()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.label.config(text=f"Selected Folder: {folder_path}")
        self.dicom_root_folder = folder_path

    def process_dicom(self):
        if hasattr(self, 'dicom_root_folder'):
            remove_phi(self.dicom_root_folder)
        else:
            self.label.config(text="Please select a DICOM root folder first.")

def run_gui():
    root = Tk()
    root.geometry("400x200")  # Set the initial window size here (width x height)
    gui = DicomProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
