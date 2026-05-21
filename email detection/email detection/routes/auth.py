from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
from utils import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email_addr = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email_addr or not password:
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email_addr):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        conn = get_db_connection()
        c = conn.cursor()
        pw_hash = generate_password_hash(password)
        c.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                  (name, email_addr, pw_hash))
        conn.commit()
        uid = c.lastrowid
        conn.close()

        session['user_id'] = uid
        session['user_name'] = name
        session['user_email'] = email_addr
        return jsonify({"message": "Account created successfully", "user": {"name": name, "email": email_addr}})
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with this email already exists. Try signing in."}), 409

@auth_bp.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    email_addr = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email_addr or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email_addr,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "No account found with this email. Please sign up first."}), 401
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    return jsonify({"message": "Login successful", "user": {"name": user['name'], "email": user['email']}})

@auth_bp.route('/api/me', methods=['GET'])
def get_me():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": {"name": session['user_name'], "email": session['user_email']}})

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})
