from tkinter import Tk, Label, Button, filedialog
import os
from pydicom import dcmread, dcmwrite
import pydicom
from datetime import datetime

def copy_dicom_files_with_filter(scan_name, dicom_directory):
    """
    Copy DICOM files from the specified directory, excluding specified series.

    Args:
        scan_name (str): Name of the scan.
        dicom_directory (str): Path to the DICOM directory.

    Returns:
        None
    """
    # Generate the output directory name
    output_directory_name = scan_name + " PHI_REMOVED"
    current_directory = os.getcwd()  # Get the current working directory
    output_directory = os.path.join(current_directory, output_directory_name, "DICOM")  # Include "DICOM" subfolder

    # Specify the series descriptions or series numbers to exclude
    exclude_series = [
        {"description": "FUJI Basic Text SR for HL7 Radiological Report", "number": 999},
        {"description": "Screen Save", "number": 99},
        {"description": "Dose Report", "number": 999}
    ]

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
        
    # Create the "segmentation" folder in the same directory as the DICOM folder
    segmentation_folder = os.path.join(current_directory, output_directory_name, "segmentation")
    os.makedirs(segmentation_folder, exist_ok=True)

    # Read all DICOM files in the directory
    dicom_files = [dcmread(os.path.join(dicom_directory, f)) for f in os.listdir(dicom_directory)]

    # Loop through DICOM files and copy files without the specified series
    for dicom_file in dicom_files:
        series_description = dicom_file.SeriesDescription
        series_number = dicom_file.SeriesNumber

        # Check if the current series is in the exclusion list
        if any(series_description == excl["description"] or series_number == excl["number"] for excl in exclude_series):
            continue  # Skip copying files with excluded series

        # Anonymize the DICOM file
        dicom_file.PatientID = "123456789"
        dicom_file.PatientName = "ANONYMOUS"
        dicom_file.PatientBirthDate = datetime.today().strftime('%Y%m%d')

        # Create the "DICOM" subfolder within the output directory
        os.makedirs(output_directory, exist_ok=True)

        # Copy the file to the output directory
        output_file_path = os.path.join(output_directory, os.path.basename(dicom_file.filename))
        dcmwrite(output_file_path, dicom_file)

        print(f"File copied: {dicom_file.filename} to {output_file_path}")

    print(f"Output directory: {output_directory}")

def remove_phi(root_folder):
    """
    Identify DICOM files, count them, and print information about DICOMOBJ folders.

    Args:
        root_folder (str): Root folder containing DICOM files.

    Returns:
        None
    """
    dicom_series = {}  # Dictionary to store paths of DICOMOBJ folders
    dicom_count = 0    # Counter for DICOM files

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            # Skip files named "DICOMDIR"
            if file == "DICOMDIR":
                continue
            
            try:
                # Attempt to read the DICOM file
                dicom_data = dcmread(os.path.join(root, file))
                # If successful, it's a DICOM file
                dicom_count += 1  # Increment the counter
                
                # Determine the parent folder name
                parent_folder_name = os.path.basename(os.path.dirname(os.path.join(root, file)))
                
                # Check if the parent folder name is "DICOMOBJ"
                if parent_folder_name == "DICOMOBJ":
                    # Get the path of the "DICOMOBJ" folder
                    dicomobj_folder_path = os.path.dirname(os.path.join(root, file))
                    # Store the path in the dictionary
                    grandparent_folder_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(root, file)))))
                    parent_folder_name = grandparent_folder_name

                    dicom_series[dicomobj_folder_path] =  parent_folder_name

                else:
                    # Update the count of series for the parent folder
                    dicom_series[os.path.dirname(os.path.join(root, file))] = parent_folder_name

            except pydicom.errors.InvalidDicomError:
                # If an InvalidDicomError is raised, it's not a DICOM file
                continue

    # Print the total number of DICOM files
    print("Total number of DICOM files: {}".format(dicom_count))

    # Print the paths of DICOMOBJ folders and the count of series for each parent folder
    for folder_path, parent_folder_name in dicom_series.items():
        print("Parent Folder: {}, Series Path: {}".format(parent_folder_name, folder_path))
    
    for folder_path, parent_folder_name in dicom_series.items():
        # Example usage
        copy_dicom_files_with_filter(parent_folder_name, folder_path)


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


root = Tk()
root.geometry("400x200")  # Set the initial window size here (width x height)
gui = DicomProcessorGUI(root)
root.mainloop()
