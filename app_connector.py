from flask import Flask, request, jsonify, render_template_string
import uuid, random, string 
from urllib.parse import unquote

app = Flask(__name__)

# In-memory storage for scripts (for simplicity)
scripts = {}

# HTML template for the form
form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>ZPA Provisioning Key</title>
    <script>
        function submitForm(event) {
            event.preventDefault(); // Prevent the default form submission behavior
            const form = event.target;
            const formData = new FormData(form);

            // Send a POST request using Fetch API
            fetch('/generate_script', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Display the generated script URL and script content
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `
                    <h3>Generated Script URL:</h3>
                    <p><a href="${data.script_url}" target="_blank">${window.location.origin}${data.script_url}</a></p>
                    <h3>Script Content:</h3>
                    <pre>${data.script_content}</pre>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</head>
<body>
    <h1>Enter Provisioning Key</h1>
    <form onsubmit="submitForm(event)">
        <label for="provisioning_key">Provisioning Key:</label><br>
        <textarea id="provisioning_key" name="provisioning_key" rows="8" cols="100" required></textarea><br>
        <button type="submit">Generate Script</button>
    </form>
    <div id="result"></div>
</body>
</html>

"""

@app.route('/', methods=['GET'])
def index():
    # Serve the HTML form for entering the provisioning key
    return render_template_string(form_html)

@app.route('/generate_script', methods=['POST'])
def generate_script():
    # Extract the provisioning key from the form submission
    encoded_key = request.form.get('provisioning_key')
    
    # Decode the provisioning key
    provisioning_key = unquote(encoded_key)

    # Generate a unique path
    script_id = ''.join(random.choices(string.ascii_letters, k=4))

    # Create a bash script using the provisioning key
    script_content = f"""#!/bin/bash
FILE="/opt/zscaler/var"
provision_key="NULL"


if [ "$EUID" -ne 0 ]
    then echo "Run as root!!"
    exit
fi
echo "********************************************************"
echo "*                                                      *"
echo "*         Provisioning ZPA Connector                   *"
echo "*                                                      *"
echo "********************************************************"
echo 

# Stop the zpa process
echo
echo "Stopping the ZPA Process ....."; sleep 2;
sudo systemctl stop zpa-connector
echo
echo "ZPA process Stopped!"
# Remove the Already provisioned configuration
echo
echo "Removing the previous configuration ....."; sleep 2;
sudo rm -rf $FILE/*
echo
echo "Successfully removed!"


# create a new provisioning key conf
sudo touch $FILE/provision_key
chmod 644 $FILE/provision_key
sudo echo {provisioning_key} > $FILE/provision_key
sleep 2
echo
echo "Starting the service again ......" ;sleep 1
sudo systemctl start zpa-connector
sleep 2
clear
sudo watch -n 1 systemctl status zpa-connector
else
    echo "Cancelling..."
    exit
fi
    """

    # Store the script content (this should be replaced with a database for production)
    scripts[script_id] = script_content

    # Generate the unique script URL using the same Flask host
    script_url = f"/{script_id}"
    return jsonify({'script_url': script_url, 'script_content': script_content})


@app.route('/<script_id>', methods=['GET'])
def get_script(script_id):
    # Fetch the script content by ID
    script_content = scripts.get(script_id)
    if script_content:
        return script_content, 200, {'Content-Type': 'text/plain'}
    else:
        return "Script not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
