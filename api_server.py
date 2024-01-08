# This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. This license allows reusers to copy and redistribute the material in any medium or format and remix, transform, and build upon the material, as long as attribution is given to the creator. The license allows for non-commercial use only, and otherwise maintains the same freedoms as the regular CC license.
# This software, "Auto RadReport," is provided as a prototype and for informational purposes only. It is not necessarily secure or accurate and is provided "as is" without warranty of any kind. Users should use this software at their own risk.
# We make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the software or the information, products, services, or related graphics contained on the software for any purpose. Any reliance you place on such information is therefore strictly at your own risk.
# This software is not intended for use in medical diagnosis or treatment or in any activity where failure or inaccuracy of use might result in harm or loss. Users are advised that health treatment or diagnosis decisions should only be made by certified medical professionals.
# In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this software.
# By using this software, you agree to this disclaimer and assume all risks associated with its use. We encourage users to ensure they comply with local laws and regulations and to use the software ethically and responsibly.

from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/download_study', methods=['POST'])
def download_study():
    # Extract accession number from the request
    data = request.json
    accession_number = data['accession_number']

    # Call another script and pass the accession number
    # Make sure to provide the correct path to your script
    # Running the script with the accession number and capturing the output
    result = subprocess.run(["python", "download.py", accession_number], capture_output=True, text=True)

    # Return the standard output along with the message
    return "Study download initiated for accession number: " + accession_number + "\nOutput: " + result.stdout

if __name__ == '__main__':
    # Run the app on all available IPs on port 5000 (Flask default)
    # You might want to run it on a different port or restrict to localhost
    app.run(host='127.0.0.1', port=5000, debug=True)

