"""
Migration script to update from projects to chatbots.
This script will:
1. Rename the projects table to chatbots
2. Rename the project_id column in documents to chatbot_id
"""

from sqlalchemy import create_engine, text
from app.config import settings


def run_migration():
    """
    Migrate from projects to chatbots schema.
    """
    print("🔄 Starting migration: projects → chatbots...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            print("\n📊 Checking existing schema...")
            
            # Check if projects table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'projects'
                );
            """))
            projects_exists = result.scalar()
            
            # Check if chatbots table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'chatbots'
                );
            """))
            chatbots_exists = result.scalar()
            
            # Check if documents.project_id exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'documents'
                    AND column_name = 'project_id'
                );
            """))
            project_id_exists = result.scalar()
            
            # Check if documents.chatbot_id exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'documents'
                    AND column_name = 'chatbot_id'
                );
            """))
            chatbot_id_exists = result.scalar()
            
            print(f"  - projects table exists: {projects_exists}")
            print(f"  - chatbots table exists: {chatbots_exists}")
            print(f"  - documents.project_id exists: {project_id_exists}")
            print(f"  - documents.chatbot_id exists: {chatbot_id_exists}")
            
            # Migration steps
            migration_needed = False
            
            # Step 1: Rename projects table to chatbots (if needed)
            if projects_exists and not chatbots_exists:
                print("\n📝 Step 1: Renaming 'projects' table to 'chatbots'...")
                conn.execute(text("ALTER TABLE projects RENAME TO chatbots;"))
                conn.commit()
                print("  ✅ Table renamed successfully")
                migration_needed = True
            elif chatbots_exists:
                print("\n✓ Step 1: 'chatbots' table already exists")
            elif not projects_exists and not chatbots_exists:
                print("\n📝 Step 1: Creating 'chatbots' table...")
                conn.execute(text("""
                    CREATE TABLE chatbots (
                        id UUID PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        is_active BOOLEAN DEFAULT TRUE NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                        updated_at TIMESTAMP DEFAULT NOW() NOT NULL
                    );
                """))
                conn.execute(text("CREATE INDEX ix_chatbots_id ON chatbots(id);"))
                conn.execute(text("CREATE INDEX ix_chatbots_owner_id ON chatbots(owner_id);"))
                conn.commit()
                print("  ✅ Table created successfully")
                migration_needed = True
            
            # Step 2: Rename project_id to chatbot_id in documents (if needed)
            if project_id_exists and not chatbot_id_exists:
                print("\n📝 Step 2: Renaming 'project_id' to 'chatbot_id' in documents table...")
                
                # First, drop the foreign key constraint
                print("  - Dropping old foreign key constraint...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    DROP CONSTRAINT IF EXISTS documents_project_id_fkey;
                """))
                
                # Rename the column
                print("  - Renaming column...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    RENAME COLUMN project_id TO chatbot_id;
                """))
                
                # Add new foreign key constraint
                print("  - Adding new foreign key constraint...")
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD CONSTRAINT documents_chatbot_id_fkey 
                    FOREIGN KEY (chatbot_id) 
                    REFERENCES chatbots(id) 
                    ON DELETE CASCADE;
                """))
                
                conn.commit()
                print("  ✅ Column renamed and constraint updated successfully")
                migration_needed = True
            elif chatbot_id_exists:
                print("\n✓ Step 2: 'chatbot_id' column already exists")
            elif not project_id_exists and not chatbot_id_exists:
                print("\n⚠️  Step 2: Neither project_id nor chatbot_id exists in documents table")
                print("  This might be normal if documents table was just created")
            
            if migration_needed:
                print("\n✅ Migration completed successfully!")
            else:
                print("\n✅ No migration needed - schema is already up to date!")
            
            print("\n📊 Current schema:")
            print("  - chatbots table: ✅")
            print("  - documents.chatbot_id column: ✅")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
