from flask import Flask, request, jsonify
import sqlite3
import os
import urllib.parse
import random
import string
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow requests from itch.io domains
CORS(app, resources={r"/*": {"origins": [
    "https://*.itch.io", 
    "https://*.itch.zone", 
    "https://itch.io",
    "https://itch.zone",
    "https://html.itch.zone",
    "https://html-classic.itch.zone",
]}})

# Database connection
def get_db_connection():
    # Check if DATABASE_URL environment variable exists (for Heroku)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Use PostgreSQL
        import psycopg2
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(database_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn, True  # True indicates PostgreSQL
    else:
        # Use SQLite for local development
        return sqlite3.connect('users.db'), False  # False indicates SQLite

# Initialize the database
def init_db():
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    # Drop existing table if it exists
    cur.execute('DROP TABLE IF EXISTS users')
    
    # Create new table with UID and status (boolean)
    if is_postgres:
        # PostgreSQL uses boolean type
        cur.execute('''
        CREATE TABLE IF NOT EXISTS uid_map (
            uid TEXT PRIMARY KEY,
            status BOOLEAN NOT NULL DEFAULT FALSE
        )
        ''')
    else:
        # SQLite doesn't have a boolean type, using integer (0/1)
        cur.execute('''
        CREATE TABLE IF NOT EXISTS uid_map (
            uid TEXT PRIMARY KEY,
            status INTEGER NOT NULL DEFAULT 0
        )
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Generate a 10-character UID
def generate_uid(length=10):
    # Combine random choice of letters and digits to create 10-char UID
    characters = string.ascii_letters + string.digits
    uid = ''.join(random.choice(characters) for _ in range(length))
    return uid

@app.route('/uid/new', methods=['GET'])
def new_uid():
    """Create a new UID with default boolean value (false)"""
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    
    # Generate a unique UID
    while True:
        uid = generate_uid(10)
        query = f'SELECT uid FROM uid_map WHERE uid = {placeholder}'
        cur.execute(query, (uid,))
        existing = cur.fetchone()
        if not existing:
            break
    
    # Default status is false (0 for SQLite, False for PostgreSQL)
    status = False if is_postgres else 0
    query = f'INSERT INTO uid_map (uid, status) VALUES ({placeholder}, {placeholder})'
    cur.execute(query, (uid, status))
    conn.commit()
    conn.close()
    
    return jsonify({'uid': uid, 'status': False})

@app.route('/uid/<uid>', methods=['GET'])
def get_uid_status(uid):
    """Get the boolean status of a UID"""
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    query = f'SELECT status FROM uid_map WHERE uid = {placeholder}'
    cur.execute(query, (uid,))
    
    result = cur.fetchone()
    conn.close()
    
    if result:
        # Convert to boolean regardless of database type
        status = bool(result[0])
        return jsonify({'uid': uid, 'status': status})
    else:
        return jsonify({'error': 'UID not found'}), 404

@app.route('/uid/<uid>', methods=['PUT'])
def update_uid_status(uid):
    """Update the boolean status of a UID"""
    if not request.json or 'status' not in request.json:
        return jsonify({'error': 'Request must include status boolean'}), 400
    
    # Get status from request and validate it's a boolean
    try:
        status = bool(request.json['status'])
    except:
        return jsonify({'error': 'Status must be a boolean value'}), 400
    
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    
    # Check if UID exists
    query = f'SELECT uid FROM uid_map WHERE uid = {placeholder}'
    cur.execute(query, (uid,))
    existing = cur.fetchone()
    
    if not existing:
        conn.close()
        return jsonify({'error': 'UID not found'}), 404
    
    # Convert boolean to appropriate type for the database
    db_status = status if is_postgres else int(status)
    
    # Update the status
    query = f'UPDATE uid_map SET status = {placeholder} WHERE uid = {placeholder}'
    cur.execute(query, (db_status, uid))
    conn.commit()
    conn.close()
    
    return jsonify({'uid': uid, 'status': status})

@app.route('/uid', methods=['POST'])
def lookup_uid():
    """Combined endpoint for different UID operations"""
    try:
        # Request for a new UID
        if request.json and request.json.get('action') == 'new':
            return new_uid()
        
        # Request to get status of an existing UID
        elif request.json and 'uid' in request.json and request.json.get('action') == 'get':
            uid = request.json['uid']
            conn, is_postgres = get_db_connection()
            cur = conn.cursor()
            
            placeholder = '%s' if is_postgres else '?'
            query = f'SELECT status FROM uid_map WHERE uid = {placeholder}'
            cur.execute(query, (uid,))
            
            result = cur.fetchone()
            conn.close()
            
            if result:
                status = bool(result[0])
                return jsonify({'uid': uid, 'status': status})
            else:
                return jsonify({'error': 'UID not found'}), 404
        
        # Request to update status of an existing UID
        elif request.json and 'uid' in request.json and 'status' in request.json and request.json.get('action') == 'update':
            uid = request.json['uid']
            try:
                status = bool(request.json['status'])
            except:
                return jsonify({'error': 'Status must be a boolean value'}), 400
            
            conn, is_postgres = get_db_connection()
            cur = conn.cursor()
            
            placeholder = '%s' if is_postgres else '?'
            
            # Check if UID exists
            query = f'SELECT uid FROM uid_map WHERE uid = {placeholder}'
            cur.execute(query, (uid,))
            existing = cur.fetchone()
            
            if not existing:
                conn.close()
                return jsonify({'error': 'UID not found'}), 404
            
            # Convert boolean to appropriate type for the database
            db_status = status if is_postgres else int(status)
            
            # Update the status
            query = f'UPDATE uid_map SET status = {placeholder} WHERE uid = {placeholder}'
            cur.execute(query, (db_status, uid))
            conn.commit()
            conn.close()
            
            return jsonify({'uid': uid, 'status': status})
        
        else:
            return jsonify({'error': 'Invalid request'}), 400
    
    except Exception as e:
        print(f"Error in lookup_uid: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 