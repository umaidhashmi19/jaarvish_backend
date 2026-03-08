from sqlalchemy.orm import Session
from app.ingestion.file_downloader import download_file
from app.ingestion.file_loader import extract_text
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_chunks
from app.ingestion.chunk_store import store_chunks


async def run_ingestion(document: object, db: Session) -> dict:
    """
    Full ingestion pipeline for one document.
    Steps: Download → Extract → Chunk → Embed → Store
    """

    # Step 3 — Download from Supabase
    file_bytes = await download_file(document.storage_path)

    # Step 4 — Extract text using LlamaIndex
    raw_text = extract_text(file_bytes, document.original_filename)

    if not raw_text.strip():
        raise ValueError("No text could be extracted from this file.")

    # Step 5 — Chunk with overlap
    chunks = chunk_text(raw_text)

    # Step 6+7 — Embed all chunks (metadata attached in chunk_store)
    embedded_results = await embed_chunks(chunks)

    # Step 8 — Store in pgvector
    summary = store_chunks(
        db=db,
        results=embedded_results,
        document_id=str(document.id),
        chatbot_id=str(document.chatbot_id),
        user_id=str(document.uploaded_by)
    )

    return summary