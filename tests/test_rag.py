import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_graph import run_rag, build_rag_graph
from agent import chat_with_agent, direct_rag_query, clear_conversation


def test_rag_graph():
    """测试RAG Graph的核心流程"""
    print("=" * 60)
    print("测试 1: RAG Graph 核心流程")
    print("=" * 60)

    # 测试问题
    test_questions = [
        "什么是RAG技术？",
        "如何优化向量检索的效果？",
        "LangGraph有什么特点？",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n--- 测试问题 {i}: {question} ---")

        try:
            # 使用直接RAG查询
            result = direct_rag_query(question)

            print(f"✓ 查询成功")
            print(f"  - 路由: {result.get('route', 'N/A')}")
            print(f"  - 扩展策略: {result.get('expansion_type', 'N/A')}")
            print(f"  - 检索文档数: {result.get('docs_count', 0)}")
            print(f"  - Trace: {result.get('trace', {})}")

            # 显示答案预览
            answer = result.get("answer", "")
            if answer:
                preview = answer[:100] + "..." if len(answer) > 100 else answer
                print(f"  - 答案预览: {preview}")

        except Exception as e:
            print(f"✗ 查询失败: {str(e)}")

    print("\n")


def test_agent():
    """测试Agent对话"""
    print("=" * 60)
    print("测试 2: Agent 对话功能")
    print("=" * 60)

    # 模拟对话
    user_id = "test_user"
    session_id = "test_session"

    conversations = [
        "你好，请介绍一下你自己",
        "什么是向量数据库？",
        "它和传统数据库有什么区别？",
    ]

    for query in conversations:
        print(f"\n用户: {query}")

        try:
            result = chat_with_agent(query, user_id, session_id)

            if result.get("success"):
                print(f"助手: {result['answer']}")
            else:
                print(f"错误: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"✗ 对话失败: {str(e)}")

    # 测试清除对话
    print("\n--- 测试清除对话历史 ---")
    clear_result = clear_conversation(user_id, session_id)
    print(f"清除结果: {clear_result}")

    print("\n")


def test_workflow_visualization():
    """可视化展示RAG工作流"""
    print("=" * 60)
    print("测试 3: RAG 工作流可视化")
    print("=" * 60)

    print("""
RAG Graph 工作流:

    ┌─────────────────┐
    │  retrieve_initial│  ← 初始检索（向量相似度）
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ grade_documents │  ← 评估文档相关性
    └────────┬────────┘
             │
        ┌────┴────┐
        │         │
    相关 │         │ 不相关
        ▼         ▼
┌──────────────┐  ┌──────────────────┐
│generate_answer│  │ rewrite_question │  ← Step-back / HyDE
└──────────────┘  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ retrieve_expanded│  ← 扩展检索
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  generate_answer │  ← 生成最终答案
                  └──────────────────┘

三种查询重写策略:
1. step_back: 退一步思考，从通用概念层面提问
2. hyde: 生成假设的理想回答文档
3. complex: 结合step_back和hyde的复杂策略
""")


def test_individual_components():
    """测试各个独立组件"""
    print("=" * 60)
    print("测试 4: 独立组件测试")
    print("=" * 60)

    # 测试文档评分
    print("\n--- 文档评分组件 ---")
    from rag_graph import grade_documents_node, RAGstate

    test_state: RAGstate = {
        "question": "什么是机器学习？",
        "docs": [
            {
                "id": 1,
                "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
                "score": 0.95,
            },
            {
                "id": 2,
                "content": "深度学习是机器学习的一种方法，使用神经网络。",
                "score": 0.88,
            },
            {"id": 3, "content": "今天的天气很好，适合户外活动。", "score": 0.30},
        ],
    }

    try:
        # 注意：需要LLM连接才能实际测试
        print("文档评分组件已定义（需要LLM连接进行实际测试）")
        print(f"测试数据: {len(test_state['docs'])} 个文档")
    except Exception as e:
        print(f"组件测试失败: {e}")

    # 测试查询重写
    print("\n--- 查询重写组件 ---")
    print("支持的策略:")
    print("  - step_back: 退一步思考")
    print("  - hyde: 假设文档嵌入")
    print("  - complex: 组合策略")

    print("\n")


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "RAG Agent 测试套件" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    # 运行所有测试
    test_workflow_visualization()
    test_individual_components()

    # 以下测试需要实际的服务连接
    print("=" * 60)
    print("注意: 以下测试需要配置环境变量和服务连接")
    print("=" * 60)
    print("\n要运行完整测试，请:")
    print("1. 复制 .env.example 为 .env")
    print("2. 填写你的 API keys 和配置")
    print("3. 确保 Milvus 和 Redis 服务已启动")
    print("4. 运行: python test_rag.py")
    print("\n")

    # 询问是否继续测试
    try:
        response = input("是否继续运行功能测试? (y/N): ").strip().lower()
        if response in ["y", "yes"]:
            test_rag_graph()
            test_agent()
        else:
            print("跳过功能测试")
    except KeyboardInterrupt:
        print("\n测试已取消")
    except EOFError:
        # 非交互式环境
        print("非交互式环境，跳过功能测试")


if __name__ == "__main__":
    main()
