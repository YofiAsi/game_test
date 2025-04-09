# Simple UID-Name Database Server

A simple Python Flask server that manages a database mapping UIDs to names.

## Setup and Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the server:
   ```
   python app.py
   ```

The server will start at http://127.0.0.1:5000

## API Endpoints

### Get all users
- GET `/users`
- Returns: JSON array of all user objects

### Get user by UID
- GET `/users/<uid>`
- Returns: User object if found, error if not found

### Create a new user
- POST `/users`
- Body: `{"uid": "user123", "name": "John Doe"}`
- Returns: Created user object

### Update a user
- PUT `/users/<uid>`
- Body: `{"name": "Jane Doe"}`
- Returns: Updated user object

### Delete a user
- DELETE `/users/<uid>`
- Returns: `{"result": true}` on success

## Example Usage (with curl)

```bash
# Create a user
curl -X POST http://127.0.0.1:5000/users -H "Content-Type: application/json" -d '{"uid": "user123", "name": "John Doe"}'

# Get all users
curl http://127.0.0.1:5000/users

# Get a specific user
curl http://127.0.0.1:5000/users/user123

# Update a user
curl -X PUT http://127.0.0.1:5000/users/user123 -H "Content-Type: application/json" -d '{"name": "Jane Doe"}'

# Delete a user
curl -X DELETE http://127.0.0.1:5000/users/user123
``` 