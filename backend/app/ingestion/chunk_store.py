import uuid
from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk


def store_chunks(
    db: Session,
    results: list[dict],
    document_id: str,
    chatbot_id: str,
    user_id: str
) -> dict:
    """
    Save successfully embedded chunks to PostgreSQL (pgvector).
    Skips failed embeddings. Returns summary.
    """
    saved = 0
    skipped = 0

    for result in results:
        if not result["success"]:
            skipped += 1
            continue

        chunk = DocumentChunk(
            id=uuid.uuid4(),
            chatbot_id=chatbot_id,
            document_id=document_id,
            chunk_index=result["chunk_index"],
            content=result["content"],
            embedding=result["embedding"]
        )
        db.add(chunk)
        saved += 1

    db.commit()

    return {"saved": saved, "skipped": skipped}