import asyncio
import os
import dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def migrate_database():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("Starting database migration...")
        
        try:
            # Create folders table if it doesn't exist
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='folders' AND xtype='U')
                CREATE TABLE folders (
                    id INTEGER IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(100) NOT NULL,
                    color NVARCHAR(20)
                );
            """))
            print("✅ Folders table created/verified")
            
            # Add folder_id column to notes table if it doesn't exist
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'notes') AND name = 'folder_id')
                ALTER TABLE notes ADD folder_id INTEGER;
            """))
            print("✅ folder_id column added to notes table")
            
            # Add foreign key constraint
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_notes_folder_id')
                ALTER TABLE notes ADD CONSTRAINT FK_notes_folder_id 
                FOREIGN KEY (folder_id) REFERENCES folders(id);
            """))
            print("✅ Foreign key constraint added")
            
            # Add icon column to folders table if it doesn't exist
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'folders') AND name = 'icon')
                ALTER TABLE folders ADD icon NVARCHAR(10) DEFAULT '📁';
            """))
            print("✅ icon column added to folders table")
            
            # Add parent_id column to folders table if it doesn't exist
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'folders') AND name = 'parent_id')
                ALTER TABLE folders ADD parent_id INTEGER;
            """))
            print("✅ parent_id column added to folders table")
            
            # Add foreign key constraint for parent_id
            await conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_folders_parent_id')
                ALTER TABLE folders ADD CONSTRAINT FK_folders_parent_id 
                FOREIGN KEY (parent_id) REFERENCES folders(id);
            """))
            print("✅ Foreign key constraint added for folder parent_id")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise
        
        print("🎉 Database migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_database()) 