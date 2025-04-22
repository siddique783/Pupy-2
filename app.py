from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import json
import os

app = Flask(__name__)
app.secret_key = 'pupysecret123'  # Change this in production

# Dummy login
USERNAME = 'admin'
PASSWORD = 'pupy123'

# Dummy session list
with open('sessions.json') as f:
    client_sessions = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('panel'))
    return render_template('login.html')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    output = ''
    command = ''
    if request.method == 'POST':
        command = request.form['command']
        # Save to command history
        with open('history.log', 'a') as log:
            log.write(command + '\n')
        try:
            result = subprocess.run(
                ['./pupysh.py', '-c', command],
                capture_output=True,
                text=True
            )
            output = result.stdout
        except Exception as e:
            output = f"Error: {e}"

    # Load command history
    history = []
    if os.path.exists('history.log'):
        with open('history.log') as f:
            history = f.readlines()

    return render_template('panel.html', sessions=client_sessions, output=output, command=command, history=history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/api/sessions')
def api_sessions():
    try:
        result = subprocess.run(
            ['./pupysh.py', 'sessions', '-o', 'json'],
            capture_output=True, text=True
        )
        sessions = json.loads(result.stdout)
        return json.dumps(sessions)
    except Exception as e:
        return json.dumps({"error": str(e)})
