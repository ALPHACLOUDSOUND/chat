from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, send
from cryptography.fernet import Fernet
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure key in production

# Initialize SocketIO
socketio = SocketIO(app)

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Dummy data for admin approval and users
approved_users = set()
pending_users = {}
user_passwords = {}
admin_id = 7049798779  # Admin's Telegram ID
admin_password = "060901"

@app.route('/')
def index():
    if 'username' in session:
        if session['username'] == admin_id:
            # Admin view
            return render_template('admin_chat.html', pending_users=pending_users)
        elif session['username'] in approved_users:
            # User view
            return render_template('chat.html', username=session['username'])
        else:
            return "Waiting for admin approval."
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == admin_id and password == admin_password:
            session['username'] = admin_id
            return redirect(url_for('index'))
        
        if username in user_passwords and user_passwords[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        
        return "Invalid credentials"
    
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if username in user_passwords:
        return "Username already exists."
    user_passwords[username] = password
    pending_users[username] = password
    return redirect(url_for('index'))

@app.route('/approve_user/<username>')
def approve_user(username):
    if 'username' in session and session['username'] == admin_id:
        if username in pending_users:
            approved_users.add(username)
            del pending_users[username]
            return redirect(url_for('index'))
        return "User not found."
    return "Unauthorized"

@app.route('/revoke_user/<username>')
def revoke_user(username):
    if 'username' in session and session['username'] == admin_id:
        if username in approved_users:
            approved_users.remove(username)
            return redirect(url_for('index'))
        return "User not found."
    return "Unauthorized"

@socketio.on('message')
def handle_message(message):
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
