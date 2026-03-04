"""
Database migration script for Chatbot and Document models.
Creates the chatbots and documents tables with all necessary constraints and indexes.
"""

from sqlalchemy import create_engine
from app.config import settings
from app.db import Base
from app.models import User, Chatbot, Document


def run_migration():
    """
    Create all tables in the database.
    This is a simple migration - for production, use Alembic.
    """
    print("🔄 Starting database migration...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database migration completed successfully!")
        print("\nCreated/Updated tables:")
        print("  - users")
        print("  - chatbots")
        print("  - documents")
        
        print("\n📊 Database schema ready for chatbots and file uploads!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
