# 📐 System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CLIENT APPLICATION                             │
│                    (Web Browser, Mobile App, etc.)                       │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ HTTPS + JWT Token
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI APPLICATION                             │
│                         (Uvicorn ASGI Server)                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      MIDDLEWARE LAYER                          │    │
│  │  • CORS Configuration                                          │    │
│  │  • Authentication (JWT)                                        │    │
│  │  • Error Handling                                              │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                       ROUTES LAYER                             │    │
│  │  POST   /files/upload          → Upload single file           │    │
│  │  POST   /files/upload/bulk     → Upload multiple files        │    │
│  │  GET    /files/                → List files (paginated)       │    │
│  │  GET    /files/{id}            → Get file details             │    │
│  │  DELETE /files/{id}            → Delete file                  │    │
│  │  GET    /files/health/storage  → Storage health check         │    │
│  │  (upload_routes.py)                                            │    │
│  └────────────────┬───────────────────────────────────────────────┘    │
│                   │                                                      │
│                   ↓                                                      │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    CONTROLLER LAYER                            │    │
│  │  • Request Validation                                          │    │
│  │  • Parameter Conversion (str → UUID)                           │    │
│  │  • Response Formatting                                         │    │
│  │  • HTTP Status Code Management                                 │    │
│  │  (upload_controller.py)                                        │    │
│  └────────────────┬───────────────────────────────────────────────┘    │
│                   │                                                      │
│                   ↓                                                      │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     SERVICE LAYER                              │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │           UploadService                              │     │    │
│  │  │  • Business Logic                                    │     │    │
│  │  │  • Transaction Management                            │     │    │
│  │  │  • Permission Checks                                 │     │    │
│  │  │  • Orchestration                                     │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │       SupabaseStorageClient                          │     │    │
│  │  │  • Storage Operations                                │     │    │
│  │  │  • File Upload/Delete                                │     │    │
│  │  │  • URL Generation                                    │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │  (upload_service.py)                                           │    │
│  └────────────────┬───────────────────────────────────────────────┘    │
│                   │                                                      │
│                   ↓                                                      │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     UTILITIES LAYER                            │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │           FileValidator                              │     │    │
│  │  │  • Extension Validation                              │     │    │
│  │  │  • MIME Type Detection                               │     │    │
│  │  │  • Size Validation                                   │     │    │
│  │  │  • Content Validation                                │     │    │
│  │  │  • Filename Sanitization                             │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │           FileHandler                                │     │    │
│  │  │  • Process Upload                                    │     │    │
│  │  │  • Generate Unique Names                             │     │    │
│  │  │  • Storage Path Generation                           │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │  (file_handler.py)                                             │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      MODELS LAYER                              │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │  Document Model (SQLAlchemy ORM)                     │     │    │
│  │  │  • id, filename, storage_path                        │     │    │
│  │  │  • file_size, file_type, extension                   │     │    │
│  │  │  • uploaded_by → User                                │     │    │
│  │  │  • project_id → Project                              │     │    │
│  │  │  • description, tags, timestamps                     │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │  (document.py, user.py, project.py)                            │    │
│  └────────────────────────────────────────────────────────────────┘    │
└────────────────────┬───────────────────────┬───────────────────────────┘
                     │                       │
                     ↓                       ↓
      ┌──────────────────────────┐  ┌──────────────────────────┐
      │   SUPABASE STORAGE       │  │   POSTGRESQL DATABASE    │
      │                          │  │                          │
      │  Bucket: file-upload     │  │  Tables:                 │
      │                          │  │  • users                 │
      │  Structure:              │  │  • projects              │
      │  users/                  │  │  • documents             │
      │    {user_id}/            │  │                          │
      │      {year}/             │  │  Features:               │
      │        {month}/          │  │  • Indexes               │
      │          {files}         │  │  • Foreign Keys          │
      │                          │  │  • Constraints           │
      │  Features:               │  │  • Timestamps            │
      │  • CDN-backed           │  │  • Relationships         │
      │  • Public/Private        │  │                          │
      │  • Automatic backups     │  │                          │
      └──────────────────────────┘  └──────────────────────────┘
```

## Data Flow - File Upload

```
1. CLIENT REQUEST
   ↓
   POST /files/upload
   Headers: Authorization: Bearer {JWT}
   Body: multipart/form-data (file + metadata)

2. MIDDLEWARE
   ↓
   • Verify JWT token
   • Extract user from token
   • Check authentication

3. ROUTE LAYER (upload_routes.py)
   ↓
   • Parse multipart form
   • Extract file and metadata
   • Pass to controller

4. CONTROLLER LAYER (upload_controller.py)
   ↓
   • Validate request parameters
   • Convert project_id string to UUID
   • Call service method

5. SERVICE LAYER (upload_service.py)
   ↓
   ┌─────────────────────────────────────┐
   │ UploadService.upload_file()         │
   │                                     │
   │ a) Call FileHandler.process_upload()│
   │    ├→ Validate extension            │
   │    ├→ Validate MIME type            │
   │    ├→ Validate size                 │
   │    ├→ Read content                  │
   │    └→ Generate unique filename      │
   │                                     │
   │ b) Upload to Supabase Storage       │
   │    └→ SupabaseStorageClient.upload()│
   │                                     │
   │ c) Save metadata to database        │
   │    └→ Create Document record        │
   │                                     │
   │ d) Commit transaction               │
   │                                     │
   │ e) Return FileUploadResponse        │
   └─────────────────────────────────────┘

6. STORAGE & DATABASE
   ↓
   ┌──────────────────┐     ┌──────────────────┐
   │ Supabase Storage │     │ PostgreSQL       │
   │ File saved at:   │     │ Record created:  │
   │ users/xxx/       │     │ documents table  │
   │   2026/02/       │     │ with metadata    │
   │   file.pdf       │     │                  │
   └──────────────────┘     └──────────────────┘

7. RESPONSE TO CLIENT
   ↓
   Status: 201 Created
   {
     "id": "uuid",
     "filename": "document.pdf",
     "file_path": "users/.../document.pdf",
     "file_size": 1048576,
     "file_type": "application/pdf",
     "uploaded_by": "user-id",
     "uploaded_at": "2026-02-26T10:30:00",
     "public_url": "https://..."
   }
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. AUTHENTICATION LAYER                                    │
│     • JWT token validation                                  │
│     • User identity verification                            │
│     • Token expiration checks                               │
│                                                             │
│  2. AUTHORIZATION LAYER                                     │
│     • Owner-only file access                                │
│     • Permission checks                                     │
│     • Public/private file rules                             │
│                                                             │
│  3. VALIDATION LAYER                                        │
│     ┌─────────────────────────────────────────────┐        │
│     │ Extension Validation                        │        │
│     │ • Check against whitelist                   │        │
│     │ • Reject dangerous types                    │        │
│     └─────────────────────────────────────────────┘        │
│     ┌─────────────────────────────────────────────┐        │
│     │ MIME Type Validation                        │        │
│     │ • Detect from content (magic bytes)         │        │
│     │ • Prevent type spoofing                     │        │
│     └─────────────────────────────────────────────┘        │
│     ┌─────────────────────────────────────────────┐        │
│     │ Content Validation                          │        │
│     │ • Verify file is not empty                  │        │
│     │ • Check actual content matches type         │        │
│     └─────────────────────────────────────────────┘        │
│     ┌─────────────────────────────────────────────┐        │
│     │ Size Validation                             │        │
│     │ • Check against MAX_FILE_SIZE_MB            │        │
│     │ • Prevent DoS via large files               │        │
│     └─────────────────────────────────────────────┘        │
│                                                             │
│  4. SANITIZATION LAYER                                      │
│     • Filename cleaning                                     │
│     • Path traversal prevention                             │
│     • Null byte removal                                     │
│     • Length limiting                                       │
│                                                             │
│  5. STORAGE LAYER                                           │
│     • Unique filename generation                            │
│     • Organized path structure                              │
│     • No overwrites (upsert=false)                          │
│     • Isolated user directories                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Validation Pipeline

```
File Upload Request
        ↓
┌───────────────────┐
│ Filename Check    │ → Reject if no extension
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Extension Check   │ → Reject if not in whitelist
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Read Content      │ → Reject if empty
└────────┬──────────┘
         ↓
┌───────────────────┐
│ MIME Detection    │ → Detect from magic bytes
└────────┬──────────┘
         ↓
┌───────────────────┐
│ MIME Verification │ → Reject if type mismatch
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Size Check        │ → Reject if > MAX_SIZE
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Sanitize Filename │ → Clean & make unique
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Generate Path     │ → Create storage path
└────────┬──────────┘
         ↓
    ✅ VALIDATED
    Ready for Upload
```

## Component Dependencies

```
main.py
  ↓
routes/upload_routes.py
  ↓
controllers/upload_controller.py
  ↓
services/upload_service.py
  ├→ models/document.py
  ├→ utils/file_handler.py
  ├→ schemas/upload_schema.py
  └→ External: Supabase Client
       ↓
    Supabase Storage (file-upload bucket)
    PostgreSQL Database (documents table)
```

---

**Legend:**
- → : Data flow / Dependency
- ↓ : Sequential step
- ├→ : Branch / Option
- └→ : Final step
- • : List item
- ✅ : Success / Validation passed
- ❌ : Failure / Validation failed
