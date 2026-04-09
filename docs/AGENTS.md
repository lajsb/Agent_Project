# AGENTS.md - RAG Agent 项目开发指南

## 项目概述

这是一个基于 LangGraph 的智能 RAG (Retrieval-Augmented Generation) Agent 系统，支持文档导入、向量检索和多轮对话。

## 技术栈

- **LLM**: OpenAI GPT-4 (通过 LangChain 调用)
- **向量数据库**: Milvus
- **关系数据库**: PostgreSQL / SQLite (SQLAlchemy)
- **缓存**: Redis
- **工作流**: LangGraph
- **文档处理**: PyPDF, python-docx, Markdown

## 核心架构

### 1. RAG 流程 (rag_graph.py)

```
用户查询 → 初始检索 → 文档评分 ──┬── 相关文档足够 → 生成答案
                                  │
                                  └── 需要重写 → 查询重写 → 扩展检索 → 生成答案
```

**查询重写策略:**
- Step-back: 退一步思考，从通用概念层面提问
- HyDE: 生成假设的理想回答文档
- Complex: 组合策略

### 2. 文档处理管道 (document_processor.py)

```
文档文件 → 加载器 → 分块器 → Embedding → Milvus 存储
```

**支持的格式:**
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- 文本文件 (.txt, .json, 代码文件等)

**分块策略:**
- Recursive: 递归字符分块（通用）
- Markdown: 按标题层级分块
- Code: 按代码结构分块

### 3. 对话历史管理 (agent.py)

使用数据库持久化存储多轮对话：
- `PersistentMemory`: 数据库持久化实现
- `MemoryService`: 业务逻辑层
- `MemoryRepository`: 数据访问层

**数据表结构 (agent_memories):**
- id: 主键
- session_id: 会话ID
- role: 角色 (user/assistant/system)
- content: 消息内容
- metadata: JSON 元数据
- created_at: 创建时间

## 代码规范

### 导入顺序

```python
# 1. 标准库
import os
from typing import List, Dict, Any

# 2. 第三方库
from langchain.chat_models import init_chat_model
from sqlalchemy.orm import Session

# 3. 项目内部模块
from database.connection import DatabaseConnection
from rag_graph import run_rag
```

### 函数文档字符串

```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    函数简短描述

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明

    Raises:
        ValueError: 异常情况说明
    """
    pass
```

### 错误处理

```python
try:
    result = risky_operation()
except SpecificException as e:
    # 记录错误日志
    print(f"操作失败: {e}")
    # 返回友好的错误信息
    return {"success": False, "error": str(e)}
```

## 数据库模型

### AgentMemory (对话历史)

```python
class AgentMemory(Base):
    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user/assistant/system
    content = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON格式
    created_at = Column(DateTime, default=datetime.utcnow)
```

### User (用户)

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # ... 其他字段
```

## 环境变量配置

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-0613

# 数据库
DATABASE_URL=sqlite:///./rag.db
# 或 DATABASE_URL=postgresql://user:pass@localhost:5432/rag_db

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 开发流程

### 1. 添加新功能

1. 在 `database/models/` 添加模型（如需要）
2. 在 `database/repositories/` 添加仓库（如需要）
3. 在 `database/services/` 添加服务（如需要）
4. 在根目录添加业务逻辑模块
5. 更新 `agent.py` 或创建新入口
6. 编写测试脚本
7. 更新 README.md 文档

### 2. 测试

```bash
# 单元测试
python -m pytest tests/

# 功能测试
python test_rag.py
python test_ingestion.py
python test_memory.py
```

### 3. 代码检查

```bash
# 格式化
black *.py database/**/*.py

# 类型检查
mypy *.py database/

# 代码风格检查
flake8 *.py database/
```

## 常见问题

### Q: 如何调试数据库查询？

在 `database/connection.py` 中设置 `echo=True`:

```python
self.engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=True,  # 打印所有 SQL 语句
)
```

### Q: 如何清理旧的对话历史？

```python
from database.services import MemoryService
from database.connection import DatabaseConnection

db = DatabaseConnection()
session = db.get_session()
service = MemoryService(session)

# 清理30天前的数据
deleted_count = service.cleanup_old_sessions(days=30)
print(f"删除了 {deleted_count} 条记录")
```

### Q: 如何添加新的文档格式支持？

在 `document_loaders.py` 中:

1. 创建新的 Loader 类继承 `BaseLoader`
2. 实现 `load()` 方法返回 `Document` 对象
3. 在 `DirectoryLoader.LOADER_MAPPING` 中添加扩展名映射

### 4. 前端界面 (frontend/)

基于 React + TypeScript + Tailwind CSS 的苹果风格前端界面：

**技术特点:**
- 苹果设计语言 (Apple Design System)
- 大量留白、圆角设计、精致动画
- 响应式布局
- 组件化架构

**功能模块:**
- **对话页面**: 类 ChatGPT 聊天界面，支持消息气泡、历史加载
- **文档管理**: 文档导入、统计展示、集合管理
- **历史记录**: 会话列表、搜索功能、导出对话

**启动方式:**
```bash
cd frontend
npm install      # 首次运行需要安装依赖
npm run dev      # 启动开发服务器
```

**访问地址:** http://localhost:5173

**生产构建:**
```bash
npm run build    # 输出到 dist/ 目录
```

**文件结构:**
```
frontend/
├── package.json              # 项目配置
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
├── tailwind.config.js        # Tailwind 配置
├── index.html                # 入口 HTML
├── src/
│   ├── main.tsx              # 应用入口
│   ├── App.tsx               # 主应用组件
│   ├── api/                  # API 客户端
│   │   └── client.ts
│   ├── components/           # 可复用组件
│   │   ├── Button.tsx
│   │   ├── MessageBubble.tsx
│   │   └── Layout/
│   ├── pages/                # 页面组件
│   │   ├── ChatPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   └── HistoryPage.tsx
│   ├── types/                # TypeScript 类型
│   ├── utils/                # 工具函数
│   └── styles/               # 样式文件
└── README.md
```

## 下一步开发计划

- [x] 文档导入管道
- [x] 对话历史持久化
- [x] FastAPI Web 接口
- [x] 前端界面 (React + TypeScript)
- [ ] RAG 评估系统
- [ ] 多租户支持
- [ ] 增量文档更新

## 参考资料

- [LangGraph 文档](https://python.langchain.com/docs/langgraph)
- [Milvus 文档](https://milvus.io/docs)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)
