"""Debug script to check database and session issues"""

import os
from dotenv import load_dotenv

load_dotenv()

from database.connection import DatabaseConnection
from database.services import MemoryService
from database.models import AgentMemory
import json

db = DatabaseConnection()
session = db.get_session()

print("=" * 60)
print("数据库调试信息")
print("=" * 60)

# 1. 检查所有消息
try:
    all_messages = session.query(AgentMemory).all()
    print(f"\n1. 总消息数: {len(all_messages)}")

    if all_messages:
        print("\n2. 最近的5条消息:")
        for msg in all_messages[-5:]:
            metadata = json.loads(msg.metadata) if msg.metadata else {}
            print(f"   - Session: {msg.session_id}")
            print(f"     Role: {msg.role}")
            print(f"     Content: {msg.content[:50]}...")
            print(f"     Metadata: {metadata}")
            print(f"     Created: {msg.created_at}")
            print()

    # 2. 检查所有不同的 session_id
    sessions = session.query(AgentMemory.session_id).distinct().all()
    print(f"3. 不同 Session 数量: {len(sessions)}")
    print(f"   Session IDs: {[s[0] for s in sessions]}")

    # 3. 检查 metadata 中的 user_id
    print("\n4. 检查 metadata 中的 user_id:")
    for msg in all_messages:
        metadata = json.loads(msg.metadata) if msg.metadata else {}
        user_id = metadata.get("user_id", "NOT SET")
        print(f"   Session {msg.session_id}: user_id={user_id}")

    # 4. 测试 get_user_sessions
    print("\n5. 测试 get_user_sessions 方法:")
    service = MemoryService(session)

    # 获取所有不同的 user_id
    all_user_ids = set()
    for msg in all_messages:
        metadata = json.loads(msg.metadata) if msg.metadata else {}
        user_id = metadata.get("user_id")
        if user_id:
            all_user_ids.add(user_id)

    print(f"   数据库中的 user_ids: {all_user_ids}")

    # 测试查询每个 user_id
    for user_id in all_user_ids:
        conversations = service.get_user_sessions(user_id)
        print(f"   User '{user_id}' 的会话数: {len(conversations)}")
        for conv in conversations:
            print(f"     - {conv['session_id']}: {conv['message_count']} messages")

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()

finally:
    session.close()

print("\n" + "=" * 60)
print("调试完成")
print("=" * 60)
