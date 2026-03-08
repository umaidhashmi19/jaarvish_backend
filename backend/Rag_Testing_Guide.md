# RAG Pipeline Testing Guide

## Packages Used

```txt
# RAG & Ingestion
llama-index-core
llama-index-readers-file
llama-index-embeddings-huggingface
sentence-transformers
groq
pgvector
httpx
```

---

## How to Test

### 1. Start Server
```bash
python -m uvicorn app.main:app --reload
```

### 2. Open Swagger
```
http://127.0.0.1:8000/docs
```

### 3. Login & Authorize
- `POST /auth/login` → enter your credentials
- Click 🔒 **Authorize** → enter username & password → click **Authorize**

### 4. Create a Chatbot
`POST /chatbots`
```json
{
  "name": "Test Bot"
}
```
Copy the `id` → this is your `chatbot_id`

### 5. Upload a File
`POST /files/upload`
- `file` → choose any PDF or TXT
- `chatbot_id` → paste your chatbot_id

Check terminal — you should see:
```
[worker] ✅ Done — X chunks saved, 0 skipped.
```

### 6. Ask a Question
`POST /chat/query`
```json
{
  "chatbot_id": "YOUR_CHATBOT_ID",
  "question": "What is this document about?"
}
```

Expected response:
```json
{
  "answer": "This document is about...",
  "chatbot_id": "...",
  "question": "What is this document about?"
}
```

---

## Confirm in Supabase SQL Editor

### Check chunks were saved
```sql
SELECT chunk_index, LEFT(content, 100) as preview, embedding IS NOT NULL as has_embedding
FROM document_chunks
ORDER BY chunk_index;
```
✅ You should see rows with `has_embedding = true`

### Check document status
```sql
SELECT id, original_filename, processing_status, error_message
FROM documents
ORDER BY uploaded_at DESC
LIMIT 5;
```
✅ `processing_status` should be `completed`

### Check which chatbot has chunks
```sql
SELECT chatbot_id, COUNT(*) as total_chunks
FROM document_chunks
GROUP BY chatbot_id;
```

---

## If Something Goes Wrong

| Problem | Fix |
|---|---|
| `[worker]` never appears in terminal | `trigger_ingestion()` not called in upload service |
| `processing_status = failed` | Check `error_message` column in documents table |
| `has_embedding = false` | Embedder failed — check terminal logs |
| No rows in `document_chunks` | Re-upload the file |
