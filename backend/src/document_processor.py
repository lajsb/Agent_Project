"""Document Processor - 文档处理管道

完整的文档处理流程：
1. 加载文档 document_loader.py files -> list[Document]
2. 分割文本 text_splitter.py
3. 生成向量 embeddings.py
4. 存入数据库 milvus_client.py + db/connection.py
"""

import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from backend.src.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv

from langchain_core.documents import Document
from backend.src.document_loaders import load_document, load_directory
from backend.src.text_splitter import TextChunk, get_splitter_for_document

load_dotenv()


@dataclass
class ProcessedChunk:
    """处理后的块数据"""

    chunk_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    source_doc: str
    chunk_index: int


class DocumentProcessor:
    """文档处理器 - 完整的文档处理管道"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small",
        batch_size: int = 100,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size

        # 初始化 embedding 模型 - 使用 DashScope
        self.embeddings = DashScopeEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", embedding_model),
            api_key=os.getenv("EMBEDDING_API_KEY"),
            base_url=os.getenv(
                "EMBEDDING_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        )

    def process_file(
        self, file_path: str, custom_metadata: Optional[Dict] = None
    ) -> List[ProcessedChunk]:
        """
        处理单个文件

        Args:
            file_path: 文件路径
            custom_metadata: 自定义元数据

        Returns:
            处理后的块列表
        """
        print(f"处理文件: {file_path}")

        # 1. 加载文档（可能返回多个文档，如PDF多页）
        docs = load_document(file_path)
        if not docs:
            return []

        all_processed_chunks = []

        for doc in docs:
            # 合并元数据
            metadata = doc.metadata.copy()
            if custom_metadata:
                metadata.update(custom_metadata)

            # 2. 分割文本
            chunks = self._split_document(doc, metadata)
            print(f"  分割成 {len(chunks)} 个块")

            # 3. 生成向量
            processed_chunks = self._generate_embeddings(
                chunks, doc.metadata.get("source", file_path)
            )
            print(f"  生成 {len(processed_chunks)} 个向量")

            all_processed_chunks.extend(processed_chunks)

        print(f"  文件处理完成，共 {len(all_processed_chunks)} 个块")
        return all_processed_chunks

    def process_directory(
        self,
        directory: str,
        glob_pattern: str = "**/*",
        custom_metadata: Optional[Dict] = None,
    ) -> List[ProcessedChunk]:
        """
        批量处理目录

        Args:
            directory: 目录路径
            glob_pattern: 文件匹配模式
            custom_metadata: 自定义元数据

        Returns:
            所有处理后的块列表
        """
        print(f"处理目录: {directory}")

        # 加载所有文档
        docs = load_directory(directory, glob_pattern)
        print(f"找到 {len(docs)} 个文档")

        all_chunks = []
        for doc in docs:
            # 合并元数据
            metadata = doc.metadata.copy()
            if custom_metadata:
                metadata.update(custom_metadata)

            # 分割文档 document ->list[TextChunk]
            chunks = self._split_document(doc, metadata)
            all_chunks.extend(chunks)

        print(f"总共分割成 {len(all_chunks)} 个块")

        # 批量生成向量
        processed_chunks = self._generate_embeddings_batch(all_chunks)
        print(f"生成了 {len(processed_chunks)} 个向量")

        return processed_chunks

    def _split_document(self, doc: Document, metadata: Dict) -> List[TextChunk]:
        """分割文档为块

        Args:
            doc: LangChain Document 对象，包含 page_content 和 metadata
            metadata: 合并后的元数据

        Returns:
            TextChunk 列表，包含内容、索引、位置和元数据
        """
        doc_type = metadata.get("doc_type", "text")

        # 获取合适的分块器
        splitter = get_splitter_for_document(
            doc_type, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        # 分割文本（LangChain Document 使用 page_content）
        chunks = splitter.split_text(doc.page_content, metadata)

        # 添加来源信息到元数据
        source = metadata.get("source", metadata.get("file_path", ""))
        for chunk in chunks:
            chunk.metadata["source"] = source
            chunk.metadata["chunk_id"] = chunk.chunk_id

        return chunks

    def _generate_embeddings(self, chunks: List[TextChunk], source: str) -> List[ProcessedChunk]:
        """为块生成向量（单批次）"""
        if not chunks:
            return []

        # 批量生成向量
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embeddings.embed_documents(texts)

        # 创建处理后的块
        processed = []
        for chunk, embedding in zip(chunks, embeddings):
            processed.append(
                ProcessedChunk(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    embedding=embedding,
                    metadata=chunk.metadata,
                    source_doc=source,
                    chunk_index=chunk.index,
                )
            )

        return processed

    def _generate_embeddings_batch(self, chunks: List[TextChunk]) -> List[ProcessedChunk]:
        """批量生成向量（多批次处理）"""
        if not chunks:
            return []

        all_processed = []

        # 按批次处理
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            print(
                f"  处理批次 {i // self.batch_size + 1}/{(len(chunks) - 1) // self.batch_size + 1} ({len(batch)} 个块)"
            )

            processed = self._generate_embeddings(batch, batch[0].metadata.get("source", ""))
            all_processed.extend(processed)

        return all_processed


class DocumentStore:
    """文档存储 - 将处理后的数据存入数据库"""

    def __init__(self):
        # 延迟导入，避免循环依赖
        from backend.milvus.client import get_milvus_client

        self.milvus = get_milvus_client()

        # 确保集合存在
        self._ensure_collection()

    def _ensure_collection(self):
        """确保Milvus集合存在"""
        collection_name = "document_chunks"

        # DashScope text-embedding-v3 维度是 1024
        dimension = 1024

        try:
            self.milvus.create_collection(collection_name, dimension)
            print(f"集合 {collection_name} 准备就绪 (维度: {dimension})")
        except Exception as e:
            print(f"集合已存在或创建失败: {e}")

    def store_chunks(self, chunks: List[ProcessedChunk]) -> Dict[str, Any]:
        """
        存储处理后的块到数据库

        Args:
            chunks: 处理后的块列表

        Returns:
            存储结果统计
        """
        if not chunks:
            return {"stored_count": 0, "errors": []}

        stored_count = 0
        errors = []

        # 准备 Milvus 数据
        milvus_ids = []
        milvus_embeddings = []
        milvus_contents = []
        milvus_metadatas = []
        milvus_sources = []
        milvus_doc_types = []

        for chunk in chunks:
            try:
                milvus_ids.append(chunk.chunk_id)
                milvus_embeddings.append(chunk.embedding)
                milvus_contents.append(chunk.content)
                milvus_metadatas.append(json.dumps(chunk.metadata, ensure_ascii=False))
                milvus_sources.append(chunk.source_doc)
                milvus_doc_types.append(chunk.metadata.get("doc_type", "text"))
                stored_count += 1
            except Exception as e:
                errors.append(f"处理块 {chunk.chunk_id} 失败: {e}")

        # 存入 Milvus
        try:
            self.milvus.insert_data_with_content(
                collection_name="document_chunks",
                ids=milvus_ids,
                embeddings=milvus_embeddings,
                contents=milvus_contents,
                metadatas=milvus_metadatas,
                sources=milvus_sources,
                doc_types=milvus_doc_types,
            )
            print(f"成功存入 {len(milvus_ids)} 个向量到 Milvus")
        except Exception as e:
            errors.append(f"Milvus 存储失败: {e}")
            print(f"Milvus 存储错误: {e}")

        return {
            "stored_count": stored_count,
            "total_chunks": len(chunks),
            "errors": errors,
        }


def process_and_store(
    file_path: Optional[str] = None,
    directory: Optional[str] = None,
    custom_metadata: Optional[Dict] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Dict[str, Any]:
    """
    便捷函数：处理并存储文档

    Args:
        file_path: 单个文件路径
        directory: 目录路径
        custom_metadata: 自定义元数据
        chunk_size: 分块大小
        chunk_overlap: 重叠大小

    Returns:
        处理结果
    """
    # 创建处理器和存储器
    processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    store = DocumentStore()

    # 处理文档
    if file_path:
        chunks = processor.process_file(file_path, custom_metadata)
    elif directory:
        chunks = processor.process_directory(directory, custom_metadata=custom_metadata)
    else:
        raise ValueError("必须提供 file_path 或 directory")

    # 存储结果
    result = store.store_chunks(chunks)

    return {
        "processed_chunks": len(chunks),
        "stored_count": result["stored_count"],
        "errors": result["errors"],
    }


# 测试代码
if __name__ == "__main__":
    print("文档处理器测试")
    print("=" * 50)

    # 创建测试文件
    test_file = "test_doc.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("# 测试文档\n\n")
        f.write("这是第一段内容。" * 20 + "\n\n")
        f.write("这是第二段内容。" * 20 + "\n\n")
        f.write("这是第三段内容。" * 20)

    # 测试处理
    try:
        result = process_and_store(
            file_path=test_file,
            custom_metadata={"category": "test", "project": "rag_agent"},
        )
        print(f"\n处理结果:")
        print(f"  处理块数: {result['processed_chunks']}")
        print(f"  存储成功: {result['stored_count']}")
        if result["errors"]:
            print(f"  错误: {result['errors']}")
    except Exception as e:
        print(f"处理失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n清理测试文件: {test_file}")
