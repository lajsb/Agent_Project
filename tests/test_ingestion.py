"""测试文档导入和处理流程"""

import os
import sys
from document_processor import process_and_store
from database_milvus_client import get_milvus_client
from rag_graph import run_rag


def test_document_ingestion():
    """测试文档导入"""
    print("=" * 60)
    print("测试文档导入")
    print("=" * 60)

    example_dir = "example_docs"

    if not os.path.exists(example_dir):
        print(f"错误: 示例目录 {example_dir} 不存在")
        return False

    try:
        # 导入示例文档
        result = process_and_store(
            directory=example_dir,
            custom_metadata={"category": "documentation", "project": "rag_demo"},
            chunk_size=800,
            chunk_overlap=150,
        )

        print(f"\n导入结果:")
        print(f"  处理块数: {result['processed_chunks']}")
        print(f"  存储成功: {result['stored_count']}")

        if result["errors"]:
            print(f"  错误数: {len(result['errors'])}")
            for err in result["errors"][:3]:
                print(f"    - {err}")

        return result["stored_count"] > 0

    except Exception as e:
        print(f"导入失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_knowledge_base_stats():
    """测试知识库统计"""
    print("\n" + "=" * 60)
    print("知识库统计")
    print("=" * 60)

    try:
        client = get_milvus_client()
        collections = client.list_collections()

        print(f"向量集合: {collections}")

        for name in collections:
            stats = client.get_collection_stats(name)
            if stats.get("exists"):
                print(f"\n  {name}:")
                print(f"    文档数: {stats.get('count', 'N/A')}")

        return True
    except Exception as e:
        print(f"获取统计失败: {e}")
        return False


def test_rag_query():
    """测试 RAG 查询"""
    print("\n" + "=" * 60)
    print("测试 RAG 查询")
    print("=" * 60)

    test_questions = [
        "什么是 RAG 技术？",
        "向量数据库有哪些种类？",
        "LangGraph 的核心概念是什么？",
    ]

    for question in test_questions:
        print(f"\n问题: {question}")
        print("-" * 40)

        try:
            result = run_rag(question)

            print(f"答案: {result['answer'][:200]}...")
            print(f"路由: {result.get('route', 'N/A')}")
            print(f"策略: {result.get('expansion_type', 'N/A')}")
            print(f"检索文档数: {result.get('docs_count', 0)}")

        except Exception as e:
            print(f"查询失败: {e}")
            import traceback

            traceback.print_exc()

    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("RAG 文档处理管道测试")
    print("=" * 60)
    print()

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: OPENAI_API_KEY 环境变量未设置")
        print("请先设置环境变量: export OPENAI_API_KEY='your-key'")
        return

    # 运行测试
    results = []

    # 测试1: 文档导入
    results.append(("文档导入", test_document_ingestion()))

    # 测试2: 知识库统计
    results.append(("知识库统计", test_knowledge_base_stats()))

    # 测试3: RAG 查询
    results.append(("RAG 查询", test_rag_query()))

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results:
        status = "通过" if passed else "失败"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("所有测试通过!" if all_passed else "部分测试失败，请检查日志"))


if __name__ == "__main__":
    main()
