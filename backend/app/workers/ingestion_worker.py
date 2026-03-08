import asyncio
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.document import Document
from app.services.ingestion_service import run_ingestion


async def process_document(document_id: str):
    """
    Background worker entry point.
    Updates document status throughout the pipeline.
    """
    db: Session = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            print(f"[worker] Document {document_id} not found.")
            return

        # Mark as processing
        document.processing_status = "processing"
        db.commit()

        # Run full ingestion pipeline
        summary = await run_ingestion(document, db)

        # Mark as completed
        document.processing_status = "completed"
        db.commit()

        print(f"[worker] ✅ Done — {summary['saved']} chunks saved, {summary['skipped']} skipped.")

    except Exception as e:
        # Mark as failed with error message
        try:
            document.processing_status = "failed"
            document.error_message = str(e)[:500]
            db.commit()
        except Exception:
            pass
        print(f"[worker] ❌ Failed for document {document_id}: {e}")

    finally:
        db.close()


def trigger_ingestion(document_id: str):
    """
    Call this from your upload route after saving the document.
    Runs the worker as a background async task.
    """
    asyncio.create_task(process_document(str(document_id)))