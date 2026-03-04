# 🚀 Quick Reference - File Upload API

## Environment Setup

```bash
# Required in .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
SUPABASE_BUCKET_NAME=file-upload
DATABASE_URL=postgresql+psycopg2://...
SECRET_KEY=your-secret-key
```

## Supabase Setup
1. Create bucket named: `file-upload`
2. Get Project URL and API Key from Settings → API

## Installation

```bash
pip install -r requirements.txt
python migrate.py
uvicorn app.main:app --reload
```

## Supported File Types

| Extension | MIME Type |
|-----------|-----------|
| .txt | text/plain |
| .md | text/markdown |
| .csv | text/csv |
| .pdf | application/pdf |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| .pptx | application/vnd.openxmlformats-officedocument.presentationml.presentation |

**Max File Size:** 50MB (configurable in .env: MAX_FILE_SIZE_MB)

## Quick API Usage

### 1. Get Token
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

### 2. Upload File
```bash
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### 3. List Files
```bash
curl http://localhost:8000/files/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Delete File
```bash
curl -X DELETE http://localhost:8000/files/{FILE_ID} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Import errors | Activate venv / install deps |
| Storage connection failed | Check SUPABASE_URL and SUPABASE_KEY |
| Bucket not found | Create 'file-upload' bucket in Supabase |
| File too large | Increase MAX_FILE_SIZE_MB in .env |
| Invalid file type | Check supported extensions list |

## File Organization

```
Supabase Storage Structure:
file-upload/
  └── users/
      └── {user_id}/
          └── {year}/
              └── {month}/
                  └── {timestamp}_{uuid}_{filename}

Example:
users/550e8400.../2026/02/20260226_a1b2c3d4_document.pdf
```

## Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Storage Health
curl http://localhost:8000/files/health/storage
```

## Interactive Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration Defaults

```python
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".docx", ".csv", ".xlsx", ".pptx", ".md"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

## Response Examples

### Upload Success
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_path": "users/.../document.pdf",
  "file_size": 1048576,
  "file_type": "application/pdf",
  "uploaded_by": "user-id",
  "uploaded_at": "2026-02-26T10:30:00",
  "public_url": null
}
```

### Error Response
```json
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

## Security Checklist

- ✅ JWT authentication required
- ✅ File extension validation
- ✅ MIME type verification
- ✅ File size limits
- ✅ Content validation
- ✅ Filename sanitization
- ✅ Owner-only deletion
- ✅ Path traversal prevention

## Testing Checklist

- [ ] Upload .txt file
- [ ] Upload .pdf file
- [ ] Upload .docx file
- [ ] Upload .csv file
- [ ] Upload .xlsx file
- [ ] Upload .pptx file
- [ ] Upload .md file
- [ ] Test file too large (>50MB)
- [ ] Test invalid file type
- [ ] Test empty file
- [ ] Test without auth token
- [ ] Test list files
- [ ] Test file details
- [ ] Test delete file
- [ ] Test bulk upload

## Key Files

| File | Purpose |
|------|---------|
| `app/routes/upload_routes.py` | API endpoints |
| `app/controllers/upload_controller.py` | Request handling |
| `app/services/upload_service.py` | Business logic |
| `app/utils/file_handler.py` | File validation |
| `app/models/document.py` | Database model |
| `app/schemas/upload_schema.py` | Request/response schemas |

## Need Help?

1. Check `IMPLEMENTATION_SUMMARY.md` for overview
2. Read `FILE_UPLOAD_README.md` for detailed docs
3. Follow `TESTING_GUIDE.md` for testing
4. Run `python setup.py` for guided setup
5. Visit `/docs` for interactive API testing
