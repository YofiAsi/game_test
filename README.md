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

### New Lookup Endpoint
- POST `/lookup`
- Supports two operations:
  1. When sending a name: `{"name": "John Doe"}`
     - If name exists: Returns the existing UID
     - If name doesn't exist: Creates a new UID and returns it
  2. When sending a UID: `{"uid": "123abc"}`
     - If UID exists: Returns the associated name
     - If UID doesn't exist: Returns "not found"

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

# Look up or create a UID for a name
curl -X POST http://127.0.0.1:5000/lookup -H "Content-Type: application/json" -d '{"name": "John Doe"}'

# Look up a name by UID
curl -X POST http://127.0.0.1:5000/lookup -H "Content-Type: application/json" -d '{"uid": "user123"}'
``` 