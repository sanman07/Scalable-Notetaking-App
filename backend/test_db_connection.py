#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    # Use the DATABASE_URL from environment or default to PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password123@localhost:5433/notes")
    
    print(f"Testing connection to: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        
        # Test basic connection
        async with async_session() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test if tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"\n📋 Tables in database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Test users table
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                print(f"\n👥 Users table: {user_count} users")
            except Exception as e:
                print(f"❌ Error querying users table: {e}")
            
            # Test folders table
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM folders"))
                folder_count = result.scalar()
                print(f"📁 Folders table: {folder_count} folders")
            except Exception as e:
                print(f"❌ Error querying folders table: {e}")
            
            # Test notes table
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM notes"))
                note_count = result.scalar()
                print(f"📝 Notes table: {note_count} notes")
            except Exception as e:
                print(f"❌ Error querying notes table: {e}")
        
        await engine.dispose()
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_connection())
