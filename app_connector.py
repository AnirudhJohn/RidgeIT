from flask import Flask, request, jsonify, render_template_string
import uuid, random, string 
from urllib.parse import unquote

app = Flask(__name__)

# In-memory storage for scripts (for simplicity)
scripts = {}

# HTML template for the form
form_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZPA App Connector Deployments Automation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            padding: 20px;
            margin: 0;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-container img {
            max-width: 100%;
            height: auto;
            max-height: 100px;
        }
        h1 {
            color: #007BFF;
            text-align: center;
            margin-bottom: 20px;
        }
        .instructions {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
            line-height: 1.6;
        }
        .instructions h2 {
            color: #007BFF;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .instructions p {
            margin: 8px 0;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        textarea {
            width: calc(100% - 20px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            margin-right: 10px;
            resize: vertical;
            font-family: monospace;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        #result {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        #result h3 {
            margin-top: 0;
            color: #007BFF;
        }
        #result p, #result pre {
            margin: 10px 0;
            word-wrap: break-word;
        }
        pre {
            background: #f1f1f1;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        code {
            font-family: monospace;
            font-size: 14px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    <script>
        function submitForm(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);

            fetch('/generate_script', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `
                    <h3>Generated Script URL:</h3>
                    <p><a href="${data.script_url}" target="_blank">${window.location.origin}${data.script_url}</a></p>
                    <h3>Command to run:</h3>
                    <pre><code>sudo su
curl ${window.location.origin}${data.script_url} | bash</code></pre>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</head>
<body>
    <div class="logo-container">
        <img src="https://cdn-ilahjpb.nitrocdn.com/jMqeUxLAqgawGnZWpPkDZlXAfrNBKXvD/assets/images/optimized/rev-c1528e3/www.ridgeit.com/wp-content/uploads/2023/05/Ridge-IT-Cyber-Logos_Ridge-blue.png" alt="Ridge IT Logo">
    </div>
    <h1>ZPA App Connector Deployments Automation</h1>
    <div class="instructions">
        <h2>Instructions:</h2>
        <p><strong>Step 1:</strong> Add the provisioning key from the ZPA Admin portal and enter it in the text area below.</p>
        <p><strong>Step 2:</strong> Run the generated commands on the app connector to provision the new connector.</p>
    </div>
    <form onsubmit="submitForm(event)">
        <label for="provisioning_key">Provisioning Key:</label>
        <textarea id="provisioning_key" name="provisioning_key" rows="8" required></textarea>
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
    # Define the content for the Zscaler repository configuration
    REPO_CONTENT="[zscaler]
name=Zscaler Private Access Repository
baseurl=https://yum.private.zscaler.com/yum/el9
enabled=1
gpgcheck=1
gpgkey=https://yum.private.zscaler.com/yum/el9/gpg"

    # Define the path for the repository file
    REPO_FILE="/etc/yum.repos.d/zscaler.repo"

    # Create or overwrite the repository file with the defined content
    echo "$REPO_CONTENT" | sudo tee "$REPO_FILE" > /dev/null


    echo "********************************************************"
    echo "*                                                      *"
    echo "*         Provisioning ZPA Connector                   *"
    echo "*                                                      *"
    echo "********************************************************"
    echo 

    # Provide feedback to the user
    echo "Zscaler repository added to $REPO_FILE"

    #Installing Zscaler App Connector Process
    yum install zpa-connector -y
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
    sudo echo "{provisioning_key}" > $FILE/provision_key
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
