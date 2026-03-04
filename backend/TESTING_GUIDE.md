# API Testing Guide

## Quick Start Testing

### 1. Start the Server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 2. Access Interactive Documentation

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test Flow

#### Step 1: Register a User

**POST** `/auth/register`

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

#### Step 2: Login

**POST** `/auth/login`

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` for subsequent requests.

#### Step 3: Upload a File

**POST** `/files/upload`

```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "description=Test upload" \
  -F "tags=test,document" \
  -F "is_public=false"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_path": "users/user-id/2026/02/20260226_a1b2c3d4_document.pdf",
  "file_size": 1048576,
  "file_type": "application/pdf",
  "uploaded_by": "user-id",
  "uploaded_at": "2026-02-26T10:30:00",
  "public_url": null
}
```

#### Step 4: List Your Files

**GET** `/files/`

```bash
curl -X GET "http://localhost:8000/files/?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "total": 5,
  "files": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "file_path": "users/user-id/2026/02/document.pdf",
      "file_size": 1048576,
      "file_type": "application/pdf",
      "uploaded_by": "user-id",
      "uploaded_at": "2026-02-26T10:30:00",
      "public_url": null
    }
  ]
}
```

#### Step 5: Get File Details

**GET** `/files/{file_id}`

```bash
curl -X GET "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Step 6: Delete a File

**DELETE** `/files/{file_id}`

```bash
curl -X DELETE "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing Different File Types

### Text Files

```bash
# Create a test file
echo "Hello, World!" > test.txt

# Upload
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.txt"
```

### Markdown Files

```bash
# Create markdown
echo "# Test Markdown" > test.md

# Upload
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.md"
```

### CSV Files

```bash
# Create CSV
echo "name,age,city\nJohn,30,NYC\nJane,25,LA" > test.csv

# Upload
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.csv"
```

## Bulk Upload Testing

**POST** `/files/upload/bulk`

```bash
curl -X POST "http://localhost:8000/files/upload/bulk" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "files=@file1.pdf" \
  -F "files=@file2.docx" \
  -F "files=@file3.xlsx" \
  -F "is_public=false"
```

**Response:**
```json
{
  "total_uploaded": 3,
  "total_failed": 0,
  "successful_uploads": [
    {...},
    {...},
    {...}
  ],
  "failed_uploads": []
}
```

## Testing Error Cases

### 1. File Too Large

```bash
# Generate a large file (over 50MB)
dd if=/dev/zero of=large_file.txt bs=1M count=51

# Try to upload (should fail)
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@large_file.txt"
```

**Expected Response:**
```json
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

### 2. Invalid File Type

```bash
# Create an executable file
echo "#!/bin/bash" > test.sh

# Try to upload (should fail)
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.sh"
```

**Expected Response:**
```json
{
  "detail": "File type '.sh' not allowed. Allowed types: .txt, .pdf, .docx, .csv, .xlsx, .pptx, .md"
}
```

### 3. Missing Authentication

```bash
# Try without token
curl -X POST "http://localhost:8000/files/upload" \
  -F "file=@test.pdf"
```

**Expected Response:**
```json
{
  "detail": "Not authenticated"
}
```

### 4. Empty File

```bash
# Create empty file
touch empty.txt

# Try to upload
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@empty.txt"
```

**Expected Response:**
```json
{
  "detail": "File is empty"
}
```

## Using Python Requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
)
print(response.json())

# 2. Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# 3. Upload file
headers = {"Authorization": f"Bearer {access_token}"}
files = {"file": open("document.pdf", "rb")}
data = {
    "description": "Test upload",
    "tags": "test,document",
    "is_public": "false"
}

response = requests.post(
    f"{BASE_URL}/files/upload",
    headers=headers,
    files=files,
    data=data
)
print(response.json())

# 4. List files
response = requests.get(
    f"{BASE_URL}/files/",
    headers=headers,
    params={"limit": 10, "offset": 0}
)
print(response.json())

# 5. Delete file
file_id = "your-file-id"
response = requests.delete(
    f"{BASE_URL}/files/{file_id}",
    headers=headers
)
print(response.json())
```

## Using Postman

### Collection Setup

1. **Create Environment:**
   - `base_url`: `http://localhost:8000`
   - `access_token`: (will be set after login)

2. **Import Collection:**
   - Use the interactive docs to generate a collection
   - Or manually create requests as shown above

3. **Set Authorization:**
   - Type: Bearer Token
   - Token: `{{access_token}}`

### Test Scripts

Add this to your Postman login request test script:

```javascript
// Extract and save access token
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
}
```

## Health Checks

### API Health

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "app": "Jaarvish API"
}
```

### Storage Health

```bash
curl http://localhost:8000/files/health/storage
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Supabase Storage",
  "bucket": "file-upload"
}
```

## Performance Testing

### Upload Speed Test

```bash
# Create 10MB test file
dd if=/dev/zero of=10mb.txt bs=1M count=10

# Time the upload
time curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@10mb.txt"
```

### Concurrent Uploads

```bash
# Upload 5 files concurrently
for i in {1..5}; do
  curl -X POST "http://localhost:8000/files/upload" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -F "file=@test$i.pdf" &
done
wait
```

## Common Issues

### 1. Import Errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### 2. Database Connection Failed
- Check DATABASE_URL in .env
- Verify Supabase credentials

### 3. Storage Upload Failed
- Verify SUPABASE_URL and SUPABASE_KEY
- Check bucket name matches SUPABASE_BUCKET_NAME
- Ensure bucket exists in Supabase

### 4. File Validation Failed
- Check file extension is allowed
- Verify file is not empty
- Ensure file size is under limit

## Next Steps

1. Test all supported file types
2. Verify error handling
3. Check authentication flow
4. Test pagination
5. Verify file ownership/permissions
6. Test bulk operations
7. Monitor storage health
8. Performance benchmarking
