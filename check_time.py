"""Check database timestamps"""

import sys

sys.path.insert(0, ".")

from backend.src.agent import get_conversation_history

result = get_conversation_history(
    user_id="user_6r630vg7", session_id="sess_gqmalc62pv5", limit=5
)

if result.get("success"):
    print("Messages found:", len(result["messages"]))
    for msg in result["messages"][:2]:
        print(f"Role: {msg['role']}")
        print(f"Created at: {msg.get('created_at')}")
        print(f"Type: {type(msg.get('created_at'))}")
        print("---")
else:
    print("Error:", result.get("error"))
