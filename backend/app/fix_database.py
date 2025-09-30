"""
Database migration script to fix the ActionStatus enum issue
Run this script to update existing 'pending' statuses to 'open'
or recreate the database with the new enum
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeting.db")

def fix_sqlite_database():
    """Fix SQLite database by recreating it"""
    print("🔧 Starting database fix for SQLite...")
    
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    # Backup existing database
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        print(f"📦 Creating backup: {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
    
    # Option 1: Delete and recreate (simplest)
    print("\n⚠️  OPTION 1: Delete database and start fresh")
    print(f"   This will delete: {db_path}")
    print("   All data will be lost!")
    
    response = input("\nDo you want to delete the database? (yes/no): ")
    
    if response.lower() == 'yes':
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Database deleted")
        
        # Recreate tables with new schema
        from app.db import engine, Base
        from app import models
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database recreated with new schema")
        print("✅ All tables created successfully")
        return
    
    # Option 2: Try to update existing data
    print("\n🔧 OPTION 2: Update existing data")
    print("   Attempting to update 'pending' status to 'open'...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # For SQLite, we need to recreate the table
            # First, check if action_items table exists
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='action_items'
            """))
            
            if result.fetchone():
                # Create a temporary table with new schema
                print("   Creating temporary table...")
                conn.execute(text("""
                    CREATE TABLE action_items_new (
                        id TEXT PRIMARY KEY,
                        meeting_id TEXT,
                        owner TEXT,
                        task TEXT NOT NULL,
                        due_date DATE,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY(meeting_id) REFERENCES meetings(id)
                    )
                """))
                
                # Copy data, converting 'pending' to 'pending' (now valid)
                print("   Copying data...")
                conn.execute(text("""
                    INSERT INTO action_items_new 
                    SELECT id, meeting_id, owner, task, due_date, 
                           CASE 
                               WHEN status = 'pending' THEN 'pending'
                               ELSE status 
                           END
                    FROM action_items
                """))
                
                # Drop old table
                print("   Dropping old table...")
                conn.execute(text("DROP TABLE action_items"))
                
                # Rename new table
                print("   Renaming table...")
                conn.execute(text("ALTER TABLE action_items_new RENAME TO action_items"))
                
                conn.commit()
                print("✅ Database updated successfully!")
            else:
                print("   No action_items table found. Creating fresh database...")
                from app.db import Base
                from app import models
                Base.metadata.create_all(bind=engine)
                print("✅ Database created successfully!")
                
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        print("\n💡 Solution: Delete the database file and restart the app")
        print(f"   Command: rm {db_path}")
        return

def fix_postgres_database():
    """Fix PostgreSQL database by altering the enum"""
    print("🔧 Starting database fix for PostgreSQL...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Add 'pending' to the enum type
            print("   Adding 'pending' to ActionStatus enum...")
            conn.execute(text("""
                ALTER TYPE actionstatus ADD VALUE IF NOT EXISTS 'pending'
            """))
            conn.commit()
            print("✅ Enum updated successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 If the enum already has 'pending', you're good to go!")
        print("   If not, you may need to recreate the enum type.")

def main():
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("Fixing ActionStatus enum issue")
    print("=" * 60)
    print(f"\nDatabase: {DATABASE_URL}\n")
    
    if DATABASE_URL.startswith("sqlite"):
        fix_sqlite_database()
    elif DATABASE_URL.startswith("postgresql"):
        fix_postgres_database()
    else:
        print("❌ Unsupported database type")
        return
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    print("\n🚀 You can now restart your FastAPI server")

if __name__ == "__main__":
    main()
