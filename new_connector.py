from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import uuid, random, string
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Hardcoded login credentials (for demonstration purposes)
USERNAME = 'testuser'
PASSWORD = 'a9Xf$7Kd!r8Jw2Q'

# In-memory storage for scripts (for simplicity)
scripts = {}

# HTML template for the login page
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            padding: 20px;
            margin: 0;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 50px auto;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input {
            width: calc(100% - 22px);
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
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
        p.error {
            color: red;
        }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Login</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <label for="username">Username:</label>
        <input type="text" name="username" required>
        <label for="password">Password:</label>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# HTML template for the form (with a logo and form structure)
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
        <img src="data:image/png;base64,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" alt="Ridge IT Logo">
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

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(login_template, error="Invalid credentials, please try again.")
    return render_template_string(login_template)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Route for the main page (requires login)
@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(form_html)

@app.route('/generate_script', methods=['POST'])
def generate_script():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    encoded_key = request.form.get('provisioning_key')
    provisioning_key = unquote(encoded_key)
    script_id = ''.join(random.choices(string.ascii_letters, k=4))

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

