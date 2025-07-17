from datetime import datetime
from flask import Flask, render_template_string, jsonify
import logging
import utils.logging
import sys

class FlaskLogBridge(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        level = record.levelno

        if level >= logging.ERROR:
            utils.logging.error(msg, name="flask")
        elif level >= logging.WARNING:
            utils.logging.warn(msg, name="flask")
        else:
            utils.logging.info(msg, name="flask")

chat_log = []
template = '''<!DOCTYPE html>
<html>
<head>
    <title>Game Chat</title>
    <style>
        body { font-family: sans-serif; }
        .msg { margin-bottom: 0.5em; }
        .author { font-weight: bold; }
        .time { color: gray; font-size: 0.9em; }
    </style>
</head>
<body>
    <h2>Live Game Chat</h2>
    <div id="chat"></div>

    <script>
        async function fetchMessages() {
            const res = await fetch('/get_msgs');
            const msgs = await res.json();
            const chat = document.getElementById('chat');
            chat.innerHTML = msgs.map(m =>
                `<div class="msg"><span class="time">[${m.time}]</span> <span class="author">${m.author}</span>: ${m.message}</div>`
            ).join('');
        }

        setInterval(fetchMessages, 2000);
    </script>
</body>
</html>'''

def send_msg(author, message):
    message = message.strip()
    if message:
        entry = {
            'author': author,
            'message': message,
            'time': datetime.now().strftime('%H:%M:%S')
        }
        chat_log.append(entry)

def get_chat_log():
    return chat_log[-50:]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(template, messages=get_chat_log())

@app.route('/get_msgs')
def get_msgs():
    return jsonify(get_chat_log())

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)
werkzeug_logger.handlers = []
werkzeug_logger.addHandler(FlaskLogBridge())
flask_app_logger = logging.getLogger('flask.app')
flask_app_logger.setLevel(logging.INFO)
flask_app_logger.handlers = []
flask_app_logger.addHandler(FlaskLogBridge())
cli = sys.modules.get('flask.cli')
if cli:
    cli.show_server_banner = lambda *args, **kwargs: None

def start(port: int):
    app.run(debug=False,port=port)
