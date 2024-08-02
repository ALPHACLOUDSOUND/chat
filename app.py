import os
import json
import string
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

# Encryption key
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Users and admin approvals
users = {}
pending_approvals = []
invite_links = []

# Admin credentials
admin_user = "alan"
admin_password = "crypto2025"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == admin_user and password == admin_password:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid credentials", 403
    return render_template('admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    return render_template('admin_dashboard.html', invite_links=invite_links)

@app.route('/admin/generate_invite', methods=['POST'])
def generate_invite():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    invite_link = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    invite_links.append(invite_link)
    return jsonify({'invite_link': invite_link})

@app.route('/admin/revoke_invite', methods=['POST'])
def revoke_invite():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    invite_link = request.form.get('invite_link')
    if invite_link in invite_links:
        invite_links.remove(invite_link)
        return jsonify({'message': 'Invite link revoked'})
    return jsonify({'error': 'Invalid invite link'}), 400

@app.route('/request_access', methods=['POST'])
def request_access():
    invite_link = request.form.get('invite_link')
    username = request.form.get('username')
    if invite_link in invite_links:
        pending_approvals.append(username)
        return jsonify({'message': 'Access requested, waiting for admin approval.'}), 200
    return jsonify({'error': 'Invalid invite link'}), 400

@app.route('/admin_approve', methods=['POST'])
def admin_approve():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    username = request.form.get('username')
    if username in pending_approvals:
        pending_approvals.remove(username)
        users[username] = {'approved': True}
        return jsonify({'message': 'User approved'}), 200
    return jsonify({'error': 'User not found in pending approvals'}), 400

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    if not users.get(username, {}).get('approved'):
        return 'Waiting for admin approval', 403
    return render_template('chat.html', username=username, encryption_key=encryption_key.decode())

@socketio.on('message')
def handle_message(data):
    username = session.get('username')
    if username and users.get(username, {}).get('approved'):
        encrypted_message = cipher.encrypt(data['message'].encode())
        emit('message', {'user': username, 'message': encrypted_message.decode()}, room='chat')
    else:
        emit('message', {'error': 'Unauthorized'})

@socketio.on('join')
def handle_join():
    join_room('chat')
    emit('message', {'user': 'system', 'message': f'{session["username"]} has joined the chat'}, room='chat')

if __name__ == '__main__':
    socketio.run(app, debug=True)
