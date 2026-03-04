# Chatbot API Guide

This guide describes all the chatbot-related APIs in the Jaarvish backend.

## Overview

The chatbot system allows users to:
- Create multiple chatbots
- Each chatbot can contain multiple documents
- Manage (create, read, update, delete) their chatbots

## Data Model

### Chatbot
- **id**: UUID (auto-generated)
- **name**: String (required, max 255 characters)
- **description**: Text (optional)
- **owner_id**: UUID (foreign key to users table)
- **is_active**: Boolean (default: true, used for soft delete)
- **created_at**: DateTime (auto-generated)
- **updated_at**: DateTime (auto-updated)

### Relationships
- One user can have many chatbots (one-to-many)
- One chatbot can have multiple documents (one-to-many)

## API Endpoints

All endpoints require authentication via JWT Bearer token.

### 1. Create Chatbot

**Endpoint**: `POST /chatbots`

**Request Body**:
```json
{
  "name": "My Chatbot",
  "description": "Optional description"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Chatbot",
  "description": "Optional description",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

### 2. List All Chatbots

**Endpoint**: `GET /chatbots`

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response** (200 OK):
```json
{
  "chatbots": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "My Chatbot",
      "description": "Optional description",
      "owner_id": "123e4567-e89b-12d3-a456-426614174000",
      "is_active": true,
      "created_at": "2026-03-04T10:30:00Z",
      "updated_at": "2026-03-04T10:30:00Z"
    }
  ],
  "total": 1
}
```

### 3. Get Chatbot by ID

**Endpoint**: `GET /chatbots/{chatbot_id}`

**Path Parameters**:
- `chatbot_id`: UUID of the chatbot

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Chatbot",
  "description": "Optional description",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Chatbot not found"
}
```

### 4. Update Chatbot

**Endpoint**: `PUT /chatbots/{chatbot_id}`

**Path Parameters**:
- `chatbot_id`: UUID of the chatbot

**Request Body** (all fields optional):
```json
{
  "name": "Updated Chatbot Name",
  "description": "Updated description",
  "is_active": true
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Chatbot Name",
  "description": "Updated description",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:35:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Chatbot not found"
}
```

### 5. Delete Chatbot

**Endpoint**: `DELETE /chatbots/{chatbot_id}`

**Path Parameters**:
- `chatbot_id`: UUID of the chatbot

**Response** (200 OK):
```json
{
  "message": "Chatbot deleted successfully"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Chatbot not found"
}
```

**Note**: This is a soft delete - the chatbot is marked as `is_active=false` but not removed from the database.

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

To get a JWT token, use the authentication endpoints:
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

## Error Responses

All endpoints may return the following error responses:

- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Resource not found or access denied
- **500 Internal Server Error**: Server-side error

## Example Usage

### Using cURL

```bash
# Create a chatbot
curl -X POST http://localhost:8000/chatbots \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Chatbot", "description": "Test chatbot"}'

# List all chatbots
curl -X GET http://localhost:8000/chatbots \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get a specific chatbot
curl -X GET http://localhost:8000/chatbots/{chatbot_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update a chatbot
curl -X PUT http://localhost:8000/chatbots/{chatbot_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete a chatbot
curl -X DELETE http://localhost:8000/chatbots/{chatbot_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Create chatbot
response = requests.post(
    f"{BASE_URL}/chatbots",
    json={"name": "My Chatbot", "description": "Test"},
    headers=headers
)
chatbot = response.json()
print(f"Created chatbot: {chatbot['id']}")

# List chatbots
response = requests.get(f"{BASE_URL}/chatbots", headers=headers)
chatbots = response.json()
print(f"Total chatbots: {chatbots['total']}")

# Get specific chatbot
chatbot_id = chatbot['id']
response = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}", headers=headers)
print(response.json())

# Update chatbot
response = requests.put(
    f"{BASE_URL}/chatbots/{chatbot_id}",
    json={"name": "Updated Name"},
    headers=headers
)
print(response.json())

# Delete chatbot
response = requests.delete(f"{BASE_URL}/chatbots/{chatbot_id}", headers=headers)
print(response.json())
```

## Database Migration

To create the chatbots table in your database, run:

```bash
python migrate.py
```

This will create/update the following tables:
- users
- chatbots
- documents

## Next Steps

After creating chatbots, you can:
1. Upload documents to specific chatbots using the `/upload` endpoints
2. Link documents to chatbots via the `chatbot_id` field
3. Query documents by chatbot
