import os
from pydicom import dcmread
import shutil
import pydicom

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
    output_directory_name = "PHI_REMOVED " + scan_name
    current_directory = os.getcwd()  # Get the current working directory
    output_directory = os.path.join(current_directory, output_directory_name)

    # Specify the series descriptions or series numbers to exclude
    exclude_series = [
        {"description": "FUJI Basic Text SR for HL7 Radiological Report", "number": 999},
        {"description": "Screen Save", "number": 99},
        {"description": "Dose Report", "number": 999}
    ]

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Read all DICOM files in the directory
    dicom_files = [dcmread(os.path.join(dicom_directory, f)) for f in os.listdir(dicom_directory)]

    # Loop through DICOM files and copy files without the specified series
    for dicom_file in dicom_files:
        series_description = dicom_file.SeriesDescription
        series_number = dicom_file.SeriesNumber

        # Check if the current series is in the exclusion list
        if any(series_description == excl["description"] or series_number == excl["number"] for excl in exclude_series):
            continue  # Skip copying files with excluded series

        # Copy the file to the output directory
        output_file_path = os.path.join(output_directory, os.path.basename(dicom_file.filename))
        shutil.copy(dicom_file.filename, output_file_path)

        print(f"File copied: {dicom_file.filename} to {output_file_path}")

    print(f"Output directory: {output_directory}")

def display_dicom_series_info(dicom_directory):
    """
    Display information about unique DICOM series in the specified directory.

    Args:
        dicom_directory (str): Path to the DICOM directory.

    Returns:
        None
    """
    # Read all DICOM files in the directory
    dicom_files = [dcmread(os.path.join(dicom_directory, f)) for f in os.listdir(dicom_directory)]

    # Dictionary to store series information and count
    series_info = {}

    # Loop through DICOM files and update the dictionary
    for dicom_file in dicom_files:
        series_description = dicom_file.SeriesDescription
        series_number = dicom_file.SeriesNumber

        # Create a unique key for each series
        series_key = (series_description, series_number)

        # Update the dictionary
        if series_key in series_info:
            series_info[series_key]["count"] += 1
        else:
            series_info[series_key] = {"description": series_description, "number": series_number, "count": 1}

    # Display unique series and count
    for series_key, info in series_info.items():
        print(f"Series Description: {info['description']}, Series Number: {info['number']}, Count: {info['count']}")

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
