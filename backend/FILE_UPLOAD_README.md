# File Upload API Documentation

## Overview

Production-ready file upload API built with FastAPI and Supabase Storage. Supports secure file uploads with comprehensive validation, organized storage, and metadata tracking.

## Supported File Types

- **Text Files**: `.txt`, `.md`
- **Documents**: `.pdf`, `.docx`
- **Spreadsheets**: `.csv`, `.xlsx`
- **Presentations**: `.pptx`

## Features

### Security & Validation
- ✅ File extension validation
- ✅ MIME type verification (prevents spoofing)
- ✅ File size limits (configurable, default 50MB)
- ✅ Content integrity checks
- ✅ Sanitized filenames
- ✅ Path traversal prevention
- ✅ Authentication & authorization

### Storage Organization
Files are stored in an organized structure:
```
users/{user_id}/{year}/{month}/{timestamp}_{uuid}_{filename}
```

### Database Tracking
- Full metadata tracking in PostgreSQL
- Soft delete support
- File relationships (users, chatbots)
- Public/private access control
- Tagging and descriptions

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Supabase Storage
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
SUPABASE_BUCKET_NAME=file-upload

# File Upload Limits
MAX_FILE_SIZE_MB=50
```

### Supabase Setup

1. **Create Storage Bucket**:
   - Go to Supabase Dashboard → Storage
   - Create a new bucket named `file-upload`
   - Configure bucket policies as needed

2. **Get API Credentials**:
   - Project URL: `https://your-project-ref.supabase.co`
   - API Key: Found in Settings → API
   - Use the `anon` key for client-side or `service_role` for server-side

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run Database Migrations**:
```bash
# The application will auto-create tables on startup
# Or use Alembic for migrations
alembic upgrade head
```

3. **Start the Server**:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### 1. Upload Single File

**POST** `/files/upload`

Upload a single file with optional metadata.

**Request**:
```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@document.pdf" \
  -F "chatbot_id=YOUR_CHATBOT_ID" \
  -F "description=Important document" \
  -F "tags=work,contract" \
  -F "is_public=false"
```

**Response**:
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

### 2. Upload Multiple Files

**POST** `/files/upload/bulk`

Upload multiple files in one request.

**Request**:
```bash
curl -X POST "http://localhost:8000/files/upload/bulk" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "files=@file1.pdf" \
  -F "files=@file2.docx" \
  -F "files=@file3.xlsx" \
  -F "chatbot_id=YOUR_CHATBOT_ID" \
  -F "is_public=false"
```

**Response**:
```json
{
  "total_uploaded": 3,
  "total_failed": 0,
  "successful_uploads": [...],
  "failed_uploads": []
}
```

### 3. List Files

**GET** `/files/`

Get paginated list of uploaded files.

**Query Parameters**:
- `chatbot_id` (optional): Filter by chatbot
- `limit` (default: 100): Maximum results
- `offset` (default: 0): Pagination offset

**Request**:
```bash
curl -X GET "http://localhost:8000/files/?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "total": 45,
  "files": [...]
}
```

### 4. Get File Details

**GET** `/files/{file_id}`

Get detailed information about a specific file.

**Request**:
```bash
curl -X GET "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Delete File

**DELETE** `/files/{file_id}`

Delete a file (soft delete + storage removal).

**Request**:
```bash
curl -X DELETE "http://localhost:8000/files/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "success": true,
  "message": "File deleted successfully",
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 6. Storage Health Check

**GET** `/files/health/storage`

Check Supabase storage connectivity.

**Request**:
```bash
curl -X GET "http://localhost:8000/files/health/storage"
```

## Architecture

The implementation follows a clean, layered architecture:

```
Routes (upload_routes.py)
    ↓
Controllers (upload_controller.py)
    ↓
Services (upload_service.py)
    ↓
Models (document.py) + Storage (Supabase)
    ↓
Database (PostgreSQL)
```

### Components

1. **Routes Layer**: HTTP endpoint definitions, request/response handling
2. **Controller Layer**: Request validation, parameter conversion
3. **Service Layer**: Business logic, transaction management
4. **Utils**: File validation, security checks
5. **Models**: Database schema and ORM
6. **Schemas**: Pydantic models for validation

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - Payload Too Large
- `500` - Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

## Security Best Practices

1. **Authentication Required**: All endpoints require valid JWT token
2. **File Validation**: Multi-layer validation (extension, MIME, content)
3. **Size Limits**: Configurable maximum file size
4. **Filename Sanitization**: Prevents path traversal attacks
5. **Access Control**: Users can only access their own files
6. **Soft Deletes**: Files can be recovered if needed

## Testing

Use the interactive API documentation:

```bash
# Start server
uvicorn app.main:app --reload

# Visit Swagger UI
http://localhost:8000/docs

# Or ReDoc
http://localhost:8000/redoc
```

## Scaling Considerations

### Current Implementation
- Files stored in Supabase Storage (CDN-backed)
- Metadata in PostgreSQL (connection pooling)
- Organized file structure for easy management

### Future Enhancements
- [ ] Virus scanning integration
- [ ] Image thumbnail generation
- [ ] File compression
- [ ] Direct upload URLs (presigned)
- [ ] Automatic file type detection
- [ ] File versioning
- [ ] Bulk delete operations
- [ ] File sharing with expiration
- [ ] Download analytics

## Database Schema

### Documents Table

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    unique_filename VARCHAR(255) UNIQUE NOT NULL,
    storage_path VARCHAR(512) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    public_url TEXT,
    uploaded_by UUID REFERENCES users(id) ON DELETE CASCADE,
    chatbot_id UUID REFERENCES chatbots(id) ON DELETE CASCADE,
    description TEXT,
    tags TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'completed',
    uploaded_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);
```

## License

This is part of the Jaarvish backend project.

## Support

For issues or questions, please refer to the main project documentation.
