# Simple UID-Boolean Database Server

A simple Python Flask server that manages a database mapping UIDs to boolean values.

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

### Get a new UID
- GET `/uid/new`
- Creates a new UID with status set to false
- Returns: `{"uid": "abc123xyz", "status": false}`

### Get UID status
- GET `/uid/<uid>`
- Returns the status of the specified UID: `{"uid": "abc123xyz", "status": false}`
- Error: `{"error": "UID not found"}` (404) if UID doesn't exist

### Update UID status
- PUT `/uid/<uid>`
- Body: `{"status": true}` or `{"status": false}`
- Returns the updated UID object: `{"uid": "abc123xyz", "status": true}`
- Error: `{"error": "UID not found"}` (404) if UID doesn't exist

### Combined endpoint for UID operations
- POST `/uid`
- Supports three operations via the `action` parameter:
  1. Create a new UID: `{"action": "new"}`
     - Returns: `{"uid": "abc123xyz", "status": false}`
  2. Get UID status: `{"action": "get", "uid": "abc123xyz"}`
     - Returns: `{"uid": "abc123xyz", "status": false}`
     - Error: `{"error": "UID not found"}` (404) if UID doesn't exist
  3. Update UID status: `{"action": "update", "uid": "abc123xyz", "status": true}`
     - Returns: `{"uid": "abc123xyz", "status": true}`
     - Error: `{"error": "UID not found"}` (404) if UID doesn't exist

## Example Usage (with curl)

```bash
# Create a new UID
curl http://127.0.0.1:5000/uid/new

# Get status of a UID
curl http://127.0.0.1:5000/uid/abc123xyz

# Update status of a UID
curl -X PUT http://127.0.0.1:5000/uid/abc123xyz -H "Content-Type: application/json" -d '{"status": true}'

# Using the combined endpoint:
# Create a new UID
curl -X POST http://127.0.0.1:5000/uid -H "Content-Type: application/json" -d '{"action": "new"}'

# Get status of a UID
curl -X POST http://127.0.0.1:5000/uid -H "Content-Type: application/json" -d '{"action": "get", "uid": "abc123xyz"}'

# Update status of a UID
curl -X POST http://127.0.0.1:5000/uid -H "Content-Type: application/json" -d '{"action": "update", "uid": "abc123xyz", "status": true}'
``` 