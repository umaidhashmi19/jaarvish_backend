"""
Optional migration to make chatbot_id required (NOT NULL).
Only run this if you don't have any existing documents or if all documents have a chatbot_id.
"""

from sqlalchemy import create_engine, text
from app.config import settings


def run_migration():
    """
    Make chatbot_id NOT NULL in documents table.
    """
    print("🔄 Checking if chatbot_id can be made NOT NULL...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check for documents with NULL chatbot_id
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM documents 
                WHERE chatbot_id IS NULL;
            """))
            null_count = result.scalar()
            
            print(f"\n📊 Found {null_count} document(s) with NULL chatbot_id")
            
            if null_count > 0:
                print("\n⚠️  WARNING: Cannot make chatbot_id NOT NULL")
                print(f"   You have {null_count} document(s) without a chatbot_id")
                print("\n   Options:")
                print("   1. Delete these documents")
                print("   2. Assign them to a chatbot")
                print("   3. Keep chatbot_id as nullable (not recommended since API requires it)")
                return
            
            # Make chatbot_id NOT NULL
            print("\n📝 Making chatbot_id NOT NULL...")
            conn.execute(text("""
                ALTER TABLE documents 
                ALTER COLUMN chatbot_id SET NOT NULL;
            """))
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("   chatbot_id is now required in the documents table")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
