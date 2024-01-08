"""
Download study data from PACS
"""

# This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. This license allows reusers to copy and redistribute the material in any medium or format and remix, transform, and build upon the material, as long as attribution is given to the creator. The license allows for non-commercial use only, and otherwise maintains the same freedoms as the regular CC license.
# This software, "Auto RadReport," is provided as a prototype and for informational purposes only. It is not necessarily secure or accurate and is provided "as is" without warranty of any kind. Users should use this software at their own risk.
# We make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the software or the information, products, services, or related graphics contained on the software for any purpose. Any reliance you place on such information is therefore strictly at your own risk.
# This software is not intended for use in medical diagnosis or treatment or in any activity where failure or inaccuracy of use might result in harm or loss. Users are advised that health treatment or diagnosis decisions should only be made by certified medical professionals.
# In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this software.
# By using this software, you agree to this disclaimer and assume all risks associated with its use. We encourage users to ensure they comply with local laws and regulations and to use the software ethically and responsibly.


import os
import argparse
import pydicom



import pandas as pd
import logging
import subprocess
logging.getLogger('pynetdicom').setLevel(logging.WARNING)
import numpy as np
from PIL import Image
#from prefect.engine import signals
from pynetdicom import (
    AE, evt, build_role,
    StoragePresentationContexts,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)
from pynetdicom.sop_class import *
from typing import List, Optional, Tuple
import time
from typing import Tuple
import pytesseract
from PIL import Image, ImageOps

# Constants for the retry mechanism
MAX_RETRIES = 10 # Max number of retries
BACKOFF_FACTOR = 1  # Exponential backoff factor
INITIAL_WAIT = 60  # Initial wait time in seconds between retries

# Command parts
command = "ollama run mistral"
task = '"Make this a structured radiology report and add an impression section: $(cat output.txt)"'

# Full command
full_command = f"{command} {task}"

AE_TITLE = b'RADIOLOGY'
AE_CALLED_TITLE = 'PACS_SERVER'
PACS_ADDR = '127.0.0.1'
PACS_PORT = 12005

DICOM_ATTR_REMOVE = ['PatientID', 'PatientName', 'CurrentPatientLocation', "PatientAddress", 'PatientOrientation', 'OtherPatientIDs', 'OtherPatientNames', 'ReferringPhysicianName',]
# Constants for DICOM and data path
DICOM_PATH = os.path.join(os.getcwd(), 'studies')  # Use os.getcwd() to get the current working directory

def remove_attributes(ds):
    """
    Remove certain attributes from dicom files
    """
    
    for de in DICOM_ATTR_REMOVE:
        if de in ds:
            ds.data_element(de).value = ''
        

def handle_store(event):
    """Handle a C-STORE request event."""

    ds = event.dataset
    context = event.context

    # Add the DICOM File Meta Information
    meta = pydicom.Dataset()
    meta.MediaStorageSOPClassUID = ds.SOPClassUID
    meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
    meta.ImplementationVersionName = PYNETDICOM_IMPLEMENTATION_VERSION
    meta.TransferSyntaxUID = context.transfer_syntax

    # Add the file meta to the dataset
    ds.file_meta = meta

    # Set the transfer syntax attributes of the dataset
    ds.is_little_endian = context.transfer_syntax.is_little_endian
    ds.is_implicit_VR = context.transfer_syntax.is_implicit_VR
    
    remove_attributes(ds)

    os.makedirs(os.path.join(DICOM_PATH, ds.AccessionNumber), exist_ok=True)
    ds.save_as(os.path.join(DICOM_PATH, ds.AccessionNumber, ds.SOPInstanceUID + ".dcm"),
               write_like_original=False)

    # Return a 'Success' status
    return 0x0000


def download_study(acc_num: str, pat_id: str = '') -> str:
    """
    :param acc_num: AccessionNumber of study
    :param pat_id: PatientID
    :return: a location of downloaded study
    """
    if not acc_num:
        raise signals.FAIL('No ACC_NUM was specified')
    os.makedirs(DICOM_PATH, exist_ok=True)

    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            ae = AE(ae_title=AE_TITLE)
            handlers = [(evt.EVT_C_STORE, handle_store)]
            ae = AE(ae_title=AE_TITLE)
            ds = pydicom.Dataset()
            ds.QueryRetrieveLevel = 'STUDY'
            ds.AccessionNumber = acc_num
            ext_neg = []
            for cx in [SecondaryCaptureImageStorage]:
                 ae.add_requested_context(cx)
                 ext_neg.append(build_role(cx, scp_role=True))

            ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
            ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
            ae.add_requested_context(PatientStudyOnlyQueryRetrieveInformationModelGet)
            assoc = ae.associate(PACS_ADDR, PACS_PORT, ae_title=AE_CALLED_TITLE, ext_neg=ext_neg, evt_handlers=handlers)

            if assoc.is_established:
                responses = assoc.send_c_get(ds, StudyRootQueryRetrieveInformationModelGet)

                for (status, identifier) in responses:
                    if not status:
                        raise Exception('PACS: Connection timed out, was aborted or received invalid response')

                # Release the association
                assoc.release()
                return os.path.join(DICOM_PATH, acc_num)  # Success, return the path
            else:
                raise Exception('PACS: Could not establish association')

        except Exception as e:
            attempts += 1
            if attempts >= MAX_RETRIES:
                raise  # Reraise the last exception after max retries exceeded
            wait_time = INITIAL_WAIT * (BACKOFF_FACTOR ** attempts)
            print(f"Attempt {attempts} failed with error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)  # Wait before retrying
    return os.path.join(DICOM_PATH, acc_num)  # This should not be reached if all retries fail

def convert_dicom_to_image(input_directory, output_directory):
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith(".dcm"):
            # Construct the full file path
            file_path = os.path.join(input_directory, filename)

            # Read the DICOM image
            ds = pydicom.dcmread(file_path)

            # Convert to a PIL Image object
            # This assumes the image is monochrome
            image = Image.fromarray(ds.pixel_array)

            # Construct the output file path, change to .png
            output_file_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '.png')

            # Save the image in PNG format
            image.save(output_file_path, "PNG")

def convert_images_to_text(input_directory, output_file):
    # Create or overwrite the output file
    with open(output_file, "w") as file:
        # Loop through all files in the input directory
        for filename in os.listdir(input_directory):
            if filename.lower().endswith(".png"):
                # Construct the full file path
                image_path = os.path.join(input_directory, filename)

                # Open the image
                image = Image.open(image_path)

                # Invert the image color
                image = ImageOps.invert(image.convert('RGB'))

                # Set the image resolution to 300 DPI
                image.save('temp_image.png', dpi=(300, 300))
                image = Image.open('temp_image.png')

                # Use Tesseract to convert the image to text
                text = pytesseract.image_to_string(image)

                # Append the text to the output file
                file.write(text + "\n\n")

                # Remove temporary image
                os.remove('temp_image.png')

def main(acc_num: str):
    # Check and create the DICOM_PATH directory
    os.makedirs(DICOM_PATH, exist_ok=True)

    # Attempt to download the study
    try:
        path = download_study(acc_num)
        DICOM_PATH2 = os.path.join(DICOM_PATH, acc_num)  # Define the path to the 'dcm' subfolder
        print(f"Study downloaded successfully for Accession Number: {acc_num}")
    except Exception as e:
        print(f'Failed to download or process the DICOM for study - {acc_num}. Exception: {e}')

    # Convert dicom to image
    if os.path.exists(DICOM_PATH2):      
        PNG_PATH = os.path.join(DICOM_PATH, acc_num, 'png')  # Define the path to the 'png' subfolder
        print(PNG_PATH)
        print(DICOM_PATH2)
        convert_dicom_to_image(DICOM_PATH2, PNG_PATH)
        convert_images_to_text(PNG_PATH, 'output.txt')

        # Run the command
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the command to complete
        stdout, stderr = process.communicate()
        # Check for errors
        if process.returncode == 0:
            print("Command executed successfully!")
            print(stdout.decode())  # or do something with the output
        else:
            print("Error executing command:")
            print(stderr.decode())
    else:
        print("Dicom directory not found.")       

if __name__ == "__main__":
    # Parse the accession number from command line arguments
    parser = argparse.ArgumentParser(description='Download DICOM files from PACS.')
    parser.add_argument('accession_number', type=str, help='Accession Number of the study to download')
    args = parser.parse_args()

    # Call main function with the provided accession number
    main(args.accession_number)