from flask import Flask, request, jsonify
import sqlite3
import os
import urllib.parse
import uuid
import random
import string

app = Flask(__name__)

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
        return conn
    else:
        # Use SQLite for local development
        return sqlite3.connect('users.db')

# Initialize the database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if DATABASE_URL environment variable exists (for Heroku)
    if os.environ.get('DATABASE_URL'):
        # PostgreSQL syntax
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')
    else:
        # SQLite syntax
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT uid, name FROM users')
    
    # Check if DATABASE_URL environment variable exists (for Heroku)
    if os.environ.get('DATABASE_URL'):
        # For PostgreSQL
        users = [{'uid': row[0], 'name': row[1]} for row in cur.fetchall()]
    else:
        # For SQLite
        users = [{'uid': row[0], 'name': row[1]} for row in cur.fetchall()]
    
    conn.close()
    return jsonify(users)

@app.route('/users/<uid>', methods=['GET'])
def get_user(uid):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT uid, name FROM users WHERE uid = %s', (uid,))
    user = cur.fetchone()
    conn.close()
    
    if user:
        return jsonify({'uid': user[0], 'name': user[1]})
    return jsonify({'error': 'User not found'}), 404

@app.route('/users', methods=['POST'])
def create_user():
    if not request.json or 'uid' not in request.json or 'name' not in request.json:
        return jsonify({'error': 'Request must include uid and name'}), 400
    
    uid = request.json['uid']
    name = request.json['name']
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Use %s as placeholder for both SQLite and PostgreSQL
        cur.execute('INSERT INTO users (uid, name) VALUES (%s, %s)', (uid, name))
        conn.commit()
        conn.close()
        return jsonify({'uid': uid, 'name': name}), 201
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        conn.close()
        return jsonify({'error': 'User with this uid already exists'}), 400

@app.route('/users/<uid>', methods=['PUT'])
def update_user(uid):
    if not request.json or 'name' not in request.json:
        return jsonify({'error': 'Request must include name'}), 400
    
    name = request.json['name']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = %s WHERE uid = %s', (name, uid))
    conn.commit()
    
    # Get row count differently for SQLite vs PostgreSQL
    rowcount = cur.rowcount
    
    if rowcount == 0:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    conn.close()
    return jsonify({'uid': uid, 'name': name})

@app.route('/users/<uid>', methods=['DELETE'])
def delete_user(uid):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE uid = %s', (uid,))
    conn.commit()
    
    # Get row count differently for SQLite vs PostgreSQL
    rowcount = cur.rowcount
    
    if rowcount == 0:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    conn.close()
    return jsonify({'result': True})

# Generate a 10-character UID
def generate_uid(length=10):
    # Combine random choice of letters and digits to create 10-char UID
    characters = string.ascii_letters + string.digits
    uid = ''.join(random.choice(characters) for _ in range(length))
    return uid

@app.route('/lookup', methods=['POST'])
def lookup():
    if not request.json:
        return jsonify({'error': 'Request must include json data'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # User is sending a name to look up or create
    if 'name' in request.json:
        name = request.json['name']
        
        # Check if name already exists
        cur.execute('SELECT uid FROM users WHERE name = %s', (name,))
        user = cur.fetchone()
        
        if user:
            # Name exists, return the UID
            uid = user[0]
            conn.close()
            return jsonify({'uid': uid})
        else:
            # Name doesn't exist, create new 10-char UID and save
            # Try to generate a unique UID (avoid collisions)
            while True:
                uid = generate_uid(10)
                # Check if this UID already exists
                cur.execute('SELECT uid FROM users WHERE uid = %s', (uid,))
                existing = cur.fetchone()
                if not existing:
                    break
            
            cur.execute('INSERT INTO users (uid, name) VALUES (%s, %s)', (uid, name))
            conn.commit()
            conn.close()
            return jsonify({'uid': uid})
    
    # User is sending a UID to look up
    elif 'uid' in request.json:
        uid = request.json['uid']
        
        # Look up UID
        cur.execute('SELECT name FROM users WHERE uid = %s', (uid,))
        user = cur.fetchone()
        
        conn.close()
        if user:
            return jsonify({'name': user[0]})
        else:
            return jsonify({'name': 'not found'})
    
    # Invalid request
    else:
        conn.close()
        return jsonify({'error': 'Request must include either name or uid'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 