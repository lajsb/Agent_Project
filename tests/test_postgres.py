"""Test PostgreSQL connection and setup"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("PostgreSQL Connection Test")
print("=" * 60)

# Check database URL
db_url = os.getenv("DATABASE_URL")
print(f"\nDatabase URL: {db_url}")

if "postgresql" not in db_url:
    print("[!] Warning: Using SQLite, please check .env file")
    print("   Should use: postgresql://rag_user:rag_password@localhost:5432/rag_db")
else:
    print("[OK] Using PostgreSQL database")

print("\nTrying to connect...")

try:
    from backend.db.connection import DatabaseConnection
    from backend.db.models import Base

    db = DatabaseConnection()

    # Test connection
    session = db.get_session()
    from sqlalchemy import text

    result = session.execute(text("SELECT version()"))
    version = result.scalar()
    print(f"[OK] Connection successful!")
    print(f"   PostgreSQL Version: {version}")

    # Create tables
    print("\nCreating tables...")
    db.create_tables(Base)
    print("[OK] Tables created")

    # Test insert
    from backend.db.services import MemoryService

    service = MemoryService(session)
    test_msg = service.add_message(
        session_id="test_session",
        role="user",
        content="Test message",
        user_id="test_user",
    )
    print(f"\n[OK] Test data inserted (ID: {test_msg['id']})")

    # Query test
    history = service.get_conversation_history("test_session")
    print(f"[OK] Query test passed (found {len(history)} messages)")

    # Clean up test data
    from backend.db.repositories import MemoryRepository

    repo = MemoryRepository(session)
    repo.clear_session("test_session")
    print("[OK] Test data cleaned up")

    session.close()

    print("\n" + "=" * 60)
    print("All tests passed! PostgreSQL is configured correctly")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPossible solutions:")
    print("1. Make sure Docker container is running: docker-compose up -d postgres")
    print("2. Check PostgreSQL logs: docker-compose logs postgres")
    print("3. Verify port 5432 is not occupied")
    print("4. Check DATABASE_URL in .env file")
    import traceback

    traceback.print_exc()
