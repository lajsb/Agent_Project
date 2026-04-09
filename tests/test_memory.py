"""测试对话历史持久化功能"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 确保数据库表存在
from database.models import Base
from database.connection import DatabaseConnection

# 创建表
db = DatabaseConnection()
Base.metadata.create_all(bind=db.engine)

from agent import (
    chat_with_agent,
    clear_conversation,
    get_conversation_history,
    list_user_conversations,
    search_conversations,
)


def test_chat_with_memory():
    """测试带记忆的对��"""
    print("=" * 60)
    print("测试对话历史持久化")
    print("=" * 60)

    user_id = "test_user_001"
    session_id = "test_session_001"

    # 先清除可能存在的旧历史
    clear_conversation(user_id, session_id)
    print(f"\n已清除旧对话历史 (user={user_id}, session={session_id})")

    # 进行多轮对话
    conversations = [
        "你好，我是测试用户",
        "什么是RAG技术？",
        "向量数据库有哪些种类？",
        "我之前问过什么？",  # 测试记忆功能
    ]

    print("\n开始多轮对话测试...\n")
    for i, query in enumerate(conversations, 1):
        print(f"第 {i} 轮:")
        print(f"  用户: {query}")

        result = chat_with_agent(query, user_id, session_id)

        if result["success"]:
            answer = result["answer"]
            print(
                f"  助手: {answer[:100]}..."
                if len(answer) > 100
                else f"  助手: {answer}"
            )
        else:
            print(f"  错误: {result.get('error', '未知错误')}")
        print()

    return user_id, session_id


def test_conversation_history(user_id: str, session_id: str):
    """测试查询对话历史"""
    print("=" * 60)
    print("测试查询对话历史")
    print("=" * 60)

    # 获取对话历史（简要格式）
    result = get_conversation_history(user_id, session_id, limit=10)

    if result["success"]:
        print(f"\n对话历史 (简要格式):")
        for msg in result["messages"]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            preview = content[:60] + "..." if len(content) > 60 else content
            print(f"  [{role}] {preview}")

        # 获取详细格式
        result_detail = get_conversation_history(
            user_id, session_id, limit=10, detail=True
        )
        if result_detail["success"]:
            print(f"\n统计信息:")
            stats = result_detail.get("stats", {})
            print(f"  总消息数: {stats.get('total_messages', 'N/A')}")
            print(f"  用户消息: {stats.get('user_messages', 'N/A')}")
            print(f"  助手消息: {stats.get('assistant_messages', 'N/A')}")
            print(f"  创建时间: {stats.get('created_at', 'N/A')}")
            print(f"  更新时间: {stats.get('updated_at', 'N/A')}")
    else:
        print(f"获取失败: {result.get('error')}")


def test_list_conversations(user_id: str):
    """测试获取用户会话列表"""
    print("\n" + "=" * 60)
    print("测试获取用户会话列表")
    print("=" * 60)

    result = list_user_conversations(user_id)

    if result["success"]:
        print(f"\n用户 {user_id} 的会话列表:")
        for conv in result["conversations"]:
            print(f"  Session: {conv['session_id']}")
            print(f"    最新消息: {conv['last_message'][:50]}...")
            print(f"    消息数: {conv['message_count']}")
            print(f"    更新时间: {conv['updated_at']}")
            print()
    else:
        print(f"获取失败: {result.get('error')}")


def test_search_conversations(user_id: str):
    """测试搜索对话内容"""
    print("=" * 60)
    print("测试搜索对话内容")
    print("=" * 60)

    keyword = "RAG"
    result = search_conversations(keyword=keyword, user_id=user_id)

    if result["success"]:
        print(f"\n搜索关键词 '{keyword}' 的结果:")
        for msg in result["results"]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            preview = content[:80] + "..." if len(content) > 80 else content
            print(f"  [{role}] {preview}")
    else:
        print(f"搜索失败: {result.get('error')}")


def test_clear_conversation(user_id: str, session_id: str):
    """测试清除对话历史"""
    print("\n" + "=" * 60)
    print("测试清除对话历史")
    print("=" * 60)

    result = clear_conversation(user_id, session_id)
    print(f"\n清除结果: {result['message']}")

    # 验证是否清除成功
    history = get_conversation_history(user_id, session_id)
    if history["success"]:
        msg_count = len(history.get("messages", []))
        print(f"验证: 剩余 {msg_count} 条消息")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("对话历史持久化功能测试")
    print("=" * 60)
    print()

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: OPENAI_API_KEY 环境变量未设置")
        print("请先设置环境变量: export OPENAI_API_KEY='your-key'")
        return

    try:
        # 测试1: 带记忆的对话
        user_id, session_id = test_chat_with_memory()

        # 测试2: 查询对话历史
        test_conversation_history(user_id, session_id)

        # 测试3: 获取用户会话列表
        test_list_conversations(user_id)

        # 测试4: 搜索对话内容
        test_search_conversations(user_id)

        # 测试5: 清除对话历史
        test_clear_conversation(user_id, session_id)

        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
