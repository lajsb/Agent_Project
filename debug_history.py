"""Debug conversation history"""

import sys

sys.path.insert(0, ".")

from backend.db.connection import DatabaseConnection
from backend.db.services import MemoryService

db = DatabaseConnection()
session = db.get_session()
service = MemoryService(session)

# Get all sessions
sessions = service.get_user_sessions("test_user", limit=10)
print(f"Found sessions: {sessions}")

# If sessions exist, get history for first one
if sessions:
    session_id = sessions[0]
    history = service.get_conversation_history(session_id, limit=10)
    print(f"\nHistory for session {session_id}:")
    print(f"Total messages: {len(history)}")
    for msg in history[:3]:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
        print(f"    created_at: {msg.get('created_at')}")

session.close()
