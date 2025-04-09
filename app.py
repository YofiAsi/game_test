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
        return conn, True  # True indicates PostgreSQL
    else:
        # Use SQLite for local development
        return sqlite3.connect('users.db'), False  # False indicates SQLite

# Initialize the database
def init_db():
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    # Same SQL works for both SQLite and PostgreSQL in this case
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
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT uid, name FROM users')
    
    users = [{'uid': row[0], 'name': row[1]} for row in cur.fetchall()]
    
    conn.close()
    return jsonify(users)

@app.route('/users/<uid>', methods=['GET'])
def get_user(uid):
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    query = f'SELECT uid, name FROM users WHERE uid = {placeholder}'
    cur.execute(query, (uid,))
    
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
    
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    
    try:
        query = f'INSERT INTO users (uid, name) VALUES ({placeholder}, {placeholder})'
        cur.execute(query, (uid, name))
        conn.commit()
        conn.close()
        return jsonify({'uid': uid, 'name': name}), 201
    except (sqlite3.IntegrityError, Exception) as e:
        conn.close()
        return jsonify({'error': 'User with this uid already exists'}), 400

@app.route('/users/<uid>', methods=['PUT'])
def update_user(uid):
    if not request.json or 'name' not in request.json:
        return jsonify({'error': 'Request must include name'}), 400
    
    name = request.json['name']
    
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    query = f'UPDATE users SET name = {placeholder} WHERE uid = {placeholder}'
    cur.execute(query, (name, uid))
    conn.commit()
    
    rowcount = cur.rowcount
    
    if rowcount == 0:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    conn.close()
    return jsonify({'uid': uid, 'name': name})

@app.route('/users/<uid>', methods=['DELETE'])
def delete_user(uid):
    conn, is_postgres = get_db_connection()
    cur = conn.cursor()
    
    placeholder = '%s' if is_postgres else '?'
    query = f'DELETE FROM users WHERE uid = {placeholder}'
    cur.execute(query, (uid,))
    conn.commit()
    
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
    try:
        if not request.json:
            return jsonify({'error': 'Request must include json data'}), 400
        
        conn, is_postgres = get_db_connection()
        cur = conn.cursor()
        
        # Use the correct placeholder based on database type
        placeholder = '%s' if is_postgres else '?'
        
        # User is sending a name to look up or create
        if 'name' in request.json:
            name = request.json['name']
            
            # Check if name already exists
            query = f'SELECT uid FROM users WHERE name = {placeholder}'
            cur.execute(query, (name,))
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
                    query = f'SELECT uid FROM users WHERE uid = {placeholder}'
                    cur.execute(query, (uid,))
                    existing = cur.fetchone()
                    if not existing:
                        break
                
                query = f'INSERT INTO users (uid, name) VALUES ({placeholder}, {placeholder})'
                cur.execute(query, (uid, name))
                conn.commit()
                conn.close()
                return jsonify({'uid': uid})
        
        # User is sending a UID to look up
        elif 'uid' in request.json:
            uid = request.json['uid']
            
            # Look up UID
            query = f'SELECT name FROM users WHERE uid = {placeholder}'
            cur.execute(query, (uid,))
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
    except Exception as e:
        print(f"Error in lookup: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 