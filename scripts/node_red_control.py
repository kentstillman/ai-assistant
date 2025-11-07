#!/usr/bin/env python3
"""
Assistant Control Panel
Web interface for managing home automation and scripts
"""

from flask import Flask, render_template_string
import subprocess
import time

app = Flask(__name__)

# Shared CSS for all pages
SHARED_STYLE = """
    body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 50px auto;
        padding: 20px;
        background-color: #f5f5f5;
    }
    h1 {
        color: #8f0000;
        text-align: center;
        margin-bottom: 10px;
    }
    h2 {
        color: #555;
        border-bottom: 2px solid #8f0000;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    .nav {
        text-align: center;
        margin: 20px 0;
        padding: 10px;
        background-color: white;
        border-radius: 5px;
    }
    .nav a {
        color: #8f0000;
        text-decoration: none;
        padding: 10px 20px;
        margin: 0 5px;
        border-radius: 3px;
        transition: background-color 0.3s;
    }
    .nav a:hover {
        background-color: #f0f0f0;
    }
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    .card {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none;
        color: #333;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .card-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    .card-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-desc {
        color: #666;
        font-size: 14px;
    }
    .button-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-top: 30px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    button {
        padding: 20px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
        width: 100%;
    }
    .stop-btn {
        background-color: #dc3545;
        color: white;
    }
    .stop-btn:hover {
        background-color: #c82333;
    }
    .start-btn {
        background-color: #28a745;
        color: white;
    }
    .start-btn:hover {
        background-color: #218838;
    }
    .restart-btn {
        background-color: #ffc107;
        color: black;
    }
    .restart-btn:hover {
        background-color: #e0a800;
    }
    .message {
        margin-top: 20px;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
    }
"""

# Landing page template
LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Assistant Control Panel</title>
    <style>
        """ + SHARED_STYLE + """
    </style>
</head>
<body>
    <h1>Assistant Control Panel</h1>
    <p style="text-align: center; color: #666;">Home Automation & Script Management</p>

    <div class="card-container">
        <a href="/node-red" class="card">
            <div class="card-icon">🔴</div>
            <div class="card-title">Node-RED</div>
            <div class="card-desc">Manage Node-RED service and flows</div>
        </a>

        <a href="/scripts" class="card">
            <div class="card-icon">📝</div>
            <div class="card-title">Scripts</div>
            <div class="card-desc">Run and manage Python scripts</div>
        </a>

        <a href="/database" class="card">
            <div class="card-icon">🗄️</div>
            <div class="card-title">Database</div>
            <div class="card-desc">Query and view data</div>
        </a>

        <a href="/system" class="card">
            <div class="card-icon">⚙️</div>
            <div class="card-title">System</div>
            <div class="card-desc">System information and settings</div>
        </a>
    </div>
</body>
</html>
"""

# Node-RED home page template
NODE_RED_HOME = """
<!DOCTYPE html>
<html>
<head>
    <title>Node-RED - Assistant</title>
    <style>
        """ + SHARED_STYLE + """
    </style>
</head>
<body>
    <h1>Node-RED Management</h1>
    <div class="nav">
        <a href="/">← Home</a>
    </div>

    <div class="card-container">
        <a href="/node-red/control" class="card">
            <div class="card-icon">🎛️</div>
            <div class="card-title">Control</div>
            <div class="card-desc">Start, Stop, Restart Node-RED</div>
        </a>

        <a href="/node-red/status" class="card">
            <div class="card-icon">📊</div>
            <div class="card-title">Status</div>
            <div class="card-desc">View service status (Coming soon)</div>
        </a>

        <a href="/node-red/logs" class="card">
            <div class="card-icon">📋</div>
            <div class="card-title">Logs</div>
            <div class="card-desc">View Node-RED logs (Coming soon)</div>
        </a>
    </div>
</body>
</html>
"""

# Node-RED control page template
NODE_RED_CONTROL = """
<!DOCTYPE html>
<html>
<head>
    <title>Node-RED Control - Assistant</title>
    <style>
        """ + SHARED_STYLE + """
    </style>
</head>
<body>
    <h1>Node-RED Control</h1>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/node-red">← Node-RED</a>
    </div>

    <h2>Service Controls</h2>
    <div class="button-container">
        <form method="POST" action="/node-red/control/stop">
            <button type="submit" class="stop-btn">⏹ Stop Node-RED</button>
        </form>
        <form method="POST" action="/node-red/control/start">
            <button type="submit" class="start-btn">▶ Start Node-RED</button>
        </form>
        <form method="POST" action="/node-red/control/restart">
            <button type="submit" class="restart-btn">🔄 Restart Node-RED</button>
        </form>
    </div>

    {% if message %}
    <div class="message {{ message_type }}">
        {{ message }}
    </div>
    {% endif %}
</body>
</html>
"""

# Placeholder page template
PLACEHOLDER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - Assistant</title>
    <style>
        """ + SHARED_STYLE + """
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="nav">
        <a href="/">← Home</a>
    </div>

    <div style="text-align: center; padding: 50px; background-color: white; border-radius: 10px; margin-top: 30px;">
        <div style="font-size: 48px; margin-bottom: 20px;">🚧</div>
        <h2>Coming Soon</h2>
        <p style="color: #666;">This section is under development.</p>
    </div>
</body>
</html>
"""

# Helper functions
def stop_node_red():
    """Stop node-red via systemd"""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'stop', 'nodered.service'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            time.sleep(1)
            return True, "Node-RED stopped successfully"
        else:
            return False, f"Error stopping Node-RED: {result.stderr}"
    except Exception as e:
        return False, f"Error stopping Node-RED: {str(e)}"

def start_node_red():
    """Start node-red via systemd"""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'start', 'nodered.service'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            time.sleep(2)
            return True, "Node-RED started successfully"
        else:
            return False, f"Error starting Node-RED: {result.stderr}"
    except Exception as e:
        return False, f"Error starting Node-RED: {str(e)}"

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template_string(LANDING_PAGE)

@app.route('/node-red')
def node_red_home():
    """Node-RED home page"""
    return render_template_string(NODE_RED_HOME)

@app.route('/node-red/control')
def node_red_control():
    """Node-RED control page"""
    return render_template_string(NODE_RED_CONTROL)

@app.route('/node-red/control/stop', methods=['POST'])
def node_red_stop():
    """Stop Node-RED"""
    success, message = stop_node_red()
    message_type = "success" if success else "error"
    return render_template_string(NODE_RED_CONTROL, message=message, message_type=message_type)

@app.route('/node-red/control/start', methods=['POST'])
def node_red_start():
    """Start Node-RED"""
    success, message = start_node_red()
    message_type = "success" if success else "error"
    return render_template_string(NODE_RED_CONTROL, message=message, message_type=message_type)

@app.route('/node-red/control/restart', methods=['POST'])
def node_red_restart():
    """Restart Node-RED via systemd"""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'restart', 'nodered.service'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            time.sleep(2)
            message = "Node-RED restarted successfully"
            message_type = "success"
        else:
            message = f"Error restarting Node-RED: {result.stderr}"
            message_type = "error"
    except Exception as e:
        message = f"Error restarting Node-RED: {str(e)}"
        message_type = "error"

    return render_template_string(NODE_RED_CONTROL, message=message, message_type=message_type)

# Placeholder routes
@app.route('/node-red/status')
def node_red_status():
    """Node-RED status page (placeholder)"""
    return render_template_string(PLACEHOLDER_PAGE, title="Node-RED Status")

@app.route('/node-red/logs')
def node_red_logs():
    """Node-RED logs page (placeholder)"""
    return render_template_string(PLACEHOLDER_PAGE, title="Node-RED Logs")

@app.route('/scripts')
def scripts():
    """Scripts page (placeholder)"""
    return render_template_string(PLACEHOLDER_PAGE, title="Scripts")

@app.route('/database')
def database():
    """Database page (placeholder)"""
    return render_template_string(PLACEHOLDER_PAGE, title="Database")

@app.route('/system')
def system():
    """System page (placeholder)"""
    return render_template_string(PLACEHOLDER_PAGE, title="System")

if __name__ == '__main__':
    print("Assistant Control Panel starting...")
    print("Access the control panel at: http://localhost:5000")
    print("Or from other devices: http://192.168.0.5:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
