# auto_radreport
This is a simple example of how to use Tesseract, Ollama, and Mistrial to convert screenshot images in ultrasound into a useful report. This project demonstrates the process of extracting text from images using OCR (Optical Character Recognition) with Tesseract, processing the data with Ollama, and then formatting it into a report with Mistrial.

Installation
Clone this repository and install the necessary dependencies to get started with Auto RadReport.

# Cloning the repository
git clone https://github.com/apyrros/auto_radreport

# Installing dependencies
pip install -r requirements.txt

# Usage
# Install ollama
# https://ollama.ai/
'curl https://ollama.ai/install.sh | sh'
'ollama run mistral'

# Install tesseract
'sudo apt-get install tesseract-ocr-[langcode]'
'brew install tesseract'

# python api_server.py
The api_server.py script utilizes the Flask web framework to run a lightweight server capable of handling API calls. It's designed to listen for requests, process them according to the defined routes and methods, and return responses. This server is integral for operations such as retrieving and processing DICOM images, facilitating the core functionalities of the Auto RadReport project. Flask's simplicity and flexibility make it an ideal choice for this script, ensuring quick setup and easy handling of web requests.

# download.py
The download.py script is designed to automate the process of handling DICOM screen captures from a DICOM server. Here's how it works:
Downloading DICOM Images: Initially, it connects to a specified DICOM server to download screen capture images.
Image to Text Conversion: Once the images are downloaded, the script utilizes Tesseract OCR (Optical Character Recognition) and the Python Imaging Library (PIL) to convert the image data into text. Tesseract is a powerful OCR engine that reads the text embedded in images, while PIL provides image processing capabilities.
Text Processing: After the text is extracted, it's passed to Oollama for further processing. Oollama processes the text based on a simple prompt, structuring or interpreting the information as needed.
Output: The final processed text is then printed out or can be directed to a file or another system for further use.
bash
Copy code

# requeststudy-ps360.ahk
The requeststudy-ps360.ahk script is a specialized tool designed to interface with PowerScribe 360. Its primary function is to automate the workflow as follows:
Search Accession Number: The script searches the PowerScribe 360 sidebar for a specific accession number. This number is typically used to identify a particular medical imaging study in the DICOM standard.
Sending Information: Once the accession number is located, requeststudy-ps360.ahk sends it to the server, effectively initiating the process of retrieving and processing the associated DICOM images.
This script streamlines the initial step in the imaging study retrieval process, ensuring a smooth transition from identifying the study in PowerScribe 360 to processing it on the server. The script is started by pressing F1. You will need to download autohotkey v1.1 (https://www.autohotkey.com/download/).


# License
This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. This license allows reusers to copy and redistribute the material in any medium or format and remix, transform, and build upon the material, as long as attribution is given to the creator. The license allows for non-commercial use only, and otherwise maintains the same freedoms as the regular CC license.

This software, "Auto RadReport," is provided as a prototype and for informational purposes only. It is not necessarily secure or accurate and is provided "as is" without warranty of any kind. Users should use this software at their own risk.

We make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the software or the information, products, services, or related graphics contained on the software for any purpose. Any reliance you place on such information is therefore strictly at your own risk.

This software is not intended for use in medical diagnosis or treatment or in any activity where failure or inaccuracy of use might result in harm or loss. Users are advised that health treatment or diagnosis decisions should only be made by certified medical professionals.

In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this software.

By using this software, you agree to this disclaimer and assume all risks associated with its use. We encourage users to ensure they comply with local laws and regulations and to use the software ethically and responsibly.

For more information, please visit Creative Commons Attribution-NonCommercial 4.0 International License.


