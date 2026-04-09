"""Milvus Vector Database Client - 向量数据库客户端"""

from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)
from typing import List, Optional, Dict, Any
import numpy as np
import os

# 全局连接配置
_CONNECTION_HOST = None
_CONNECTION_PORT = None
_CONNECTION_ESTABLISHED = False


class MilvusClientWrapper:
    """Milvus 客户端包装器"""

    def __init__(self, host: str = "localhost", port: int = 19530, alias: str = "default"):
        self.host = host
        self.port = port
        self.alias = alias
        self._connected = False
        self._connect()

    def _connect(self):
        """建立连接"""
        global _CONNECTION_ESTABLISHED, _CONNECTION_HOST, _CONNECTION_PORT

        try:
            from pymilvus import connections

            # 检查是否已有全局连接
            if _CONNECTION_ESTABLISHED:
                # 使用已有连接配置
                self._connected = True
                return

            # 检查是否已有同名连接，如果有则断开
            if self.alias in connections.list_connections():
                try:
                    connections.disconnect(self.alias)
                except:
                    pass

            # 建立新连接
            connections.connect(alias=self.alias, host=self.host, port=self.port)
            _CONNECTION_ESTABLISHED = True
            _CONNECTION_HOST = self.host
            _CONNECTION_PORT = self.port
            print(f"已连接到 Milvus: {self.host}:{self.port}")
            self._connected = True
        except Exception as e:
            print(f"警告: 连接 Milvus 失败: {e}")
            print("向量搜索功能将不可用，其他功能正常运行")
            self._connected = False

    def create_collection(
        self, collection_name: str, dimension: int = 1024, metric_type: str = "COSINE"
    ):
        """
        创建集合（如果不存在）

        默认维度 1024 对应 DashScope text-embedding-v3 模型

        Args:
            collection_name: 集合名称
            dimension: 向量维度（OpenAI embedding 是 1536）
            metric_type: 距离度量类型
        """
        if not self._connected:
            print(f"警告: Milvus 未连接，无法创建集合 {collection_name}")
            return None

        if utility.has_collection(collection_name, using=self.alias):
            print(f"集合 {collection_name} 已存在")
            return Collection(collection_name, using=self.alias)

        # 定义字段
        fields = [
            # 主键字段 - 使用 chunk_id
            FieldSchema(
                name="chunk_id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=64,
                description="文档块唯一标识",
            ),
            # 向量字段
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=dimension,
                description="文本向量",
            ),
            # 内容字段
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=65535,  # 最大 64KB
                description="文本内容",
            ),
            # 元数据字段
            FieldSchema(
                name="metadata",
                dtype=DataType.VARCHAR,
                max_length=4096,
                default="{}",
                description="JSON 格式的元数据",
            ),
            # 来源字段 - 用于过滤
            FieldSchema(
                name="source",
                dtype=DataType.VARCHAR,
                max_length=512,
                default="",
                description="文档来源",
            ),
            # 文档类型
            FieldSchema(
                name="doc_type",
                dtype=DataType.VARCHAR,
                max_length=64,
                default="text",
                description="文档类型",
            ),
        ]

        # 创建 schema
        schema = CollectionSchema(
            fields=fields, description="RAG 文档块向量集合", enable_dynamic_field=True
        )

        # 创建集合
        collection = Collection(name=collection_name, schema=schema, using=self.alias)

        # 创建索引
        index_params = {
            "metric_type": metric_type,
            "index_type": "IVF_FLAT",  # 或 HNSW 以获得更好性能
            "params": {"nlist": 1024},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        print(f"集合 {collection_name} 创建成功，维度: {dimension}")

        return collection

    def insert_data_with_content(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        contents: List[str],
        metadatas: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        doc_types: Optional[List[str]] = None,
    ):
        """
        插入数据到集合

        Args:
            collection_name: 集合名称
            ids: 文档块ID列表
            embeddings: 向量列表
            contents: 内容列表
            metadatas: 元数据JSON字符串列表
            sources: 来源列表
            doc_types: 文档类型列表
        """
        if not self._connected:
            print(f"警告: Milvus 未连接，无法插入数据")
            return None

        if not utility.has_collection(collection_name, using=self.alias):
            raise ValueError(f"集合 {collection_name} 不存在")

        collection = Collection(collection_name, using=self.alias)

        # 准备数据
        data = [
            ids,
            embeddings,
            contents,
            metadatas or ["{}"] * len(ids),
            sources or [""] * len(ids),
            doc_types or ["text"] * len(ids),
        ]

        # 插入数据
        insert_result = collection.insert(data)
        collection.flush()

        print(f"成功插入 {len(ids)} 条数据到 {collection_name}")
        return insert_result

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        向量搜索

        Args:
            collection_name: 集合名称
            query_embedding: 查询向量
            top_k: 返回结果数量
            filter_expr: 过滤表达式
            output_fields: 返回的字段

        Returns:
            搜索结果列表
        """
        if not self._connected:
            print(f"警告: Milvus 未连接，无法执行搜索")
            return []

        if not utility.has_collection(collection_name, using=self.alias):
            raise ValueError(f"集合 {collection_name} 不存在")

        collection = Collection(collection_name, using=self.alias)
        collection.load()

        # 搜索参数
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        # 默认返回字段
        if output_fields is None:
            output_fields = ["chunk_id", "content", "metadata", "source", "doc_type"]

        # 执行搜索
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=output_fields,
        )

        # 格式化结果
        formatted_results = []
        for hits in results:
            for hit in hits:
                result = {
                    "chunk_id": hit.entity.get("chunk_id"),
                    "content": hit.entity.get("content"),
                    "metadata": hit.entity.get("metadata"),
                    "source": hit.entity.get("source"),
                    "doc_type": hit.entity.get("doc_type"),
                    "distance": hit.distance,
                    "score": 1 - hit.distance if hit.distance <= 1 else 1 / (1 + hit.distance),
                }
                formatted_results.append(result)

        return formatted_results

    def delete_by_source(self, collection_name: str, source: str) -> int:
        """删除指定来源的所有文档"""
        if not self._connected:
            print(f"警告: Milvus 未连接，无法删除数据")
            return 0

        if not utility.has_collection(collection_name, using=self.alias):
            return 0

        collection = Collection(collection_name, using=self.alias)
        collection.load()

        try:
            # 先查询该 source 的所有文档 ID
            # 使用转义处理特殊字符
            escaped_source = source.replace("\\", "\\\\").replace('"', '\\"')
            expr = f'source == "{escaped_source}"'
            print(f"[DEBUG] Delete expr: {expr}")

            results = collection.query(
                expr=expr,
                output_fields=["chunk_id"],
            )

            if not results:
                print(f"未找到 source 为 {source} 的文档")
                return 0

            ids_to_delete = [r["chunk_id"] for r in results]
            print(f"准备删除 {len(ids_to_delete)} 条记录")

            # 分批删除
            batch_size = 100
            total_deleted = 0
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i : i + batch_size]
                ids_expr = ", ".join([f'"{id}"' for id in batch])
                result = collection.delete(f"chunk_id in [{ids_expr}]")
                total_deleted += result.delete_count

            collection.flush()
            print(f"从 {collection_name} 删除了 {total_deleted} 条记录")
            return total_deleted

        except Exception as e:
            print(f"删除失败: {e}")
            import traceback

            traceback.print_exc()
            return 0

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        if not self._connected:
            return {"exists": False, "name": collection_name, "count": 0}

        if not utility.has_collection(collection_name, using=self.alias):
            return {"exists": False}

        collection = Collection(collection_name, using=self.alias)
        collection.load()

        # 使用 query 获取实际数量，而不是 num_entities（删除后不会立即更新）
        try:
            # 分批查询统计数量（Milvus limit 最大 16384）
            total_count = 0
            offset = 0
            batch_size = 16384
            while True:
                results = collection.query(
                    expr="chunk_id != ''",
                    output_fields=["chunk_id"],
                    limit=batch_size,
                    offset=offset,
                )
                batch_count = len(results)
                total_count += batch_count
                if batch_count < batch_size:
                    break
                offset += batch_size
            actual_count = total_count
        except Exception as e:
            print(f"[WARN] Failed to query collection count: {e}")
            actual_count = collection.num_entities

        return {
            "exists": True,
            "name": collection_name,
            "count": actual_count,
            "schema": str(collection.schema),
        }

    def get_sources(self, collection_name: str) -> List[str]:
        """获取集合中所有的 source（去重）"""
        if not self._connected:
            return []

        if not utility.has_collection(collection_name, using=self.alias):
            return []

        collection = Collection(collection_name, using=self.alias)
        collection.load()

        # 分批查询所有文档的 source 字段（Milvus limit 最大 16384）
        all_results = []
        offset = 0
        batch_size = 16384
        while True:
            results = collection.query(
                expr="source != ''",
                output_fields=["source"],
                limit=batch_size,
                offset=offset,
            )
            all_results.extend(results)
            if len(results) < batch_size:
                break
            offset += batch_size

        # 去重
        sources = list(set([r["source"] for r in all_results if r.get("source")]))
        return sorted(sources)

    def clear_collection(self, collection_name: str) -> int:
        """清空整个集合的所有文档"""
        if not self._connected:
            print(f"警告: Milvus 未连接，无法清空集合")
            return 0

        if not utility.has_collection(collection_name, using=self.alias):
            return 0

        collection = Collection(collection_name, using=self.alias)
        collection.load()

        # 获取删除前的数量
        before_count = collection.num_entities
        print(f"集合 {collection_name} 当前有 {before_count} 条记录")

        if before_count == 0:
            return 0

        # 删除所有数据 - 使用更可靠的表达式
        try:
            # 分批查询所有ID（Milvus limit 最大 16384）
            ids_to_delete = []
            offset = 0
            batch_size = 16384
            while True:
                results = collection.query(
                    expr="chunk_id != ''",
                    output_fields=["chunk_id"],
                    limit=batch_size,
                    offset=offset,
                )
                ids_to_delete.extend([r["chunk_id"] for r in results])
                if len(results) < batch_size:
                    break
                offset += batch_size

            if not ids_to_delete:
                return 0

            print(f"准备删除 {len(ids_to_delete)} 条记录")

            # 分批删除（避免一次删除太多）
            batch_size = 100
            total_deleted = 0
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i : i + batch_size]
                ids_expr = ", ".join([f'"{id}"' for id in batch])
                result = collection.delete(f"chunk_id in [{ids_expr}]")
                total_deleted += result.delete_count

            # 强制刷新确保删除生效
            collection.flush()

            # 重新加载集合以更新统计
            collection.release()
            collection.load()

            # 获取删除后的数量
            after_count = collection.num_entities
            print(f"清空集合 {collection_name} 完成，删除前: {before_count}, 删除后: {after_count}")

            return total_deleted
        except Exception as e:
            print(f"清空集合失败: {e}")
            import traceback

            traceback.print_exc()
            return 0

    def list_collections(self) -> List[str]:
        """列出所有集合"""
        if not self._connected:
            return []
        return utility.list_collections(using=self.alias)


# 全局客户端实例
_milvus_client = None


def get_milvus_client() -> MilvusClientWrapper:
    """获取全局 Milvus 客户端实例"""
    global _milvus_client
    if _milvus_client is None:
        import os

        _milvus_client = MilvusClientWrapper(
            host=os.getenv("MILVUS_HOST", "localhost"),
            port=int(os.getenv("MILVUS_PORT", "19530")),
        )
    return _milvus_client


# 保持向后兼容的接口
class MilvusClientWrapperLegacy:
    """旧版接口兼容"""

    def __init__(self, host: str = "localhost", port: int = 19530):
        self._wrapper = MilvusClientWrapper(host, port)

    def create_collection(self, collection_name: str, dimension: int):
        return self._wrapper.create_collection(collection_name, dimension)

    def insert_data(self, collection_name: str, ids: List[int], embeddings: List[List[float]]):
        """旧版插入接口（仅用于兼容）"""
        return self._wrapper.insert_data_with_content(
            collection_name,
            ids=[str(i) for i in ids],
            embeddings=embeddings,
            contents=[f"Document {i}" for i in ids],
            metadatas=["{}"] * len(ids),
        )

    def search(self, collection_name: str, query_embedding: List[float], top_k: int) -> List[str]:
        """旧版搜索接口（仅返回ID）"""
        results = self._wrapper.search(
            collection_name, query_embedding, top_k, output_fields=["chunk_id"]
        )
        return [r["chunk_id"] for r in results]


# 导出兼容的旧版客户端
MilvusClient = MilvusClientWrapperLegacy("localhost", 19530)


# 测试代码
if __name__ == "__main__":
    print("Milvus 客户端测试")
    print("=" * 50)

    try:
        client = MilvusClientWrapper()

        # 列出集合
        collections = client.list_collections()
        print(f"现有集合: {collections}")

        # 创建测试集合
        collection_name = "test_collection"
        collection = client.create_collection(collection_name, dimension=1536)

        # 测试插入
        test_data = {
            "ids": ["test_1", "test_2"],
            "embeddings": [[0.1] * 1536, [0.2] * 1536],
            "contents": ["这是测试文档1", "这是测试文档2"],
            "metadatas": ['{"source": "test"}', '{"source": "test"}'],
            "sources": ["test.txt", "test.txt"],
            "doc_types": ["text", "text"],
        }

        client.insert_data_with_content(collection_name, **test_data)

        # 查询统计
        stats = client.get_collection_stats(collection_name)
        print(f"集合统计: {stats}")

        # 测试搜索
        results = client.search(collection_name, [0.1] * 1536, top_k=2)
        print(f"搜索结果: {len(results)} 条")
        for r in results:
            print(f"  - {r['chunk_id']}: {r['content'][:20]}... (score: {r['score']:.3f})")

        print("\n测试完成!")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
