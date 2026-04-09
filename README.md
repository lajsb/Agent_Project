# RAG Agent - 智能知识库助手

一个基于 RAG (Retrieval-Augmented Generation) 技术的智能对话系统，支持文档上传、向量检索和智能问答。

## 项目结构

```
rag_plus/
├── backend/              # 后端服务
│   ├── src/             # 核心业务逻辑
│   │   ├── agent.py              # AI Agent 主逻辑
│   │   ├── rag_graph.py          # RAG 流程图
│   │   ├── document_processor.py # 文档处理
│   │   ├── embeddings.py         # 向量嵌入
│   │   ├── text_splitter.py      # 文本分块
│   │   ├── document_loaders.py   # 文档加载器
│   │   └── redis_cache.py        # Redis 缓存
│   ├── api/             # API 接口
│   │   ├── main.py              # FastAPI 入口
│   │   ├── models.py            # 数据模型
│   │   └── routes/              # API 路由
│   │       ├── chat.py
│   │       └── documents.py
│   ├── db/              # 数据库
│   │   ├── connection.py        # 数据库连接
│   │   ├── models/              # ORM 模型
│   │   ├── repositories/        # 数据仓库
│   │   └── services/            # 业务服务
│   └── milvus/          # Milvus 客户端
│       └── client.py
├── frontend/            # React 前端
│   ├── src/
│   │   ├── api/         # API 客户端
│   │   ├── components/  # 可复用组件
│   │   ├── pages/       # 页面组件
│   │   ├── styles/      # 样式文件
│   │   ├── types/       # TypeScript 类型
│   │   └── utils/       # 工具函数
│   └── package.json
├── scripts/             # 工具脚本
│   ├── run_api.py       # 启动后端
│   └── ingest.py        # 文档导入
├── tests/               # 测试文件
│   ├── test_postgres.py
│   ├── test_ingestion.py
│   ├── test_memory.py
│   ├── test_rag.py
│   └── example_docs/    # 示例文档
├── docs/                # 项目文档
│   ├── README.md        # 架构说明
│   ├── deployment.md    # 部署指南
│   └── run.md          # 运行指南
├── docker/              # Docker 配置
│   └── docker-compose.yml
├── data/                # 数据卷
│   └── volumes/         # Docker 数据持久化
│       ├── postgres/    # PostgreSQL 数据
│       ├── milvus/      # Milvus 向量数据
│       ├── minio/       # MinIO 对象存储
│       └── etcd/        # Etcd 配置数据
├── .env                 # 环境变量
├── .env.example         # 环境变量示例
├── requirements.txt     # Python 依赖
└── README.md           # 本文件
```

## 快速开始

### 1. 环境准备

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose

### 2. 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 4. 启动服务

```bash
# 启动数据库（PostgreSQL + Milvus + MinIO）
docker-compose -f docker/docker-compose.yml up -d

# 启动后端
cd scripts
python run_api.py --reload

# 启动前端（新终端）
cd frontend
npm run dev
```

### 5. 访问系统

- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs

## 核心功能

### 1. 智能对话
- 基于 LangGraph 的多轮对话管理
- 支持会话隔离和历史记录
- 自适应 RAG 策略（Step-back + HyDE）

### 2. 文档管理
- 支持 PDF、Word、TXT、Markdown 等格式
- 拖拽上传或点击选择
- 自动分块和向量化

### 3. 知识库检索
- Milvus 向量数据库
- 相似度搜索 + 重排序
- 支持多集合管理

### 4. 数据存储
- PostgreSQL: 对话历史、用户数据
- Milvus: 文档向量
- MinIO: 对象存储

## 技术栈

### 后端
- **框架**: FastAPI + Uvicorn
- **AI**: LangChain + LangGraph + OpenAI API
- **数据库**: PostgreSQL + SQLAlchemy
- **向量库**: Milvus
- **缓存**: Redis (可选)

### 前端
- **框架**: React 18 + TypeScript
- **构建**: Vite
- **样式**: Tailwind CSS
- **UI**: Lucide Icons

### 基础设施
- **容器**: Docker + Docker Compose
- **向量存储**: Milvus + MinIO + Etcd

## 开发指南

### 添加新的 API 端点

1. 在 `backend/api/routes/` 创建新文件
2. 在 `backend/api/main.py` 注册路由

### 添加新的文档加载器

1. 在 `backend/src/document_loaders.py` 添加加载函数
2. 在 `backend/src/document_processor.py` 中使用

### 数据库迁移

```bash
# 自动创建表（首次运行）
python -c "
from backend.db.connection import DatabaseConnection
from backend.db.models.base import Base
db = DatabaseConnection()
db.create_tables(Base)
"
```

## 部署

### 生产环境配置

1. 使用 PostgreSQL 而非 SQLite
2. 配置 Nginx 反向代理
3. 设置 HTTPS
4. 配置环境变量（密钥、数据库连接等）

详见 [docs/deployment.md](docs/deployment.md)

## 数据备份

```bash
# 备份 PostgreSQL
docker-compose -f docker/docker-compose.yml exec postgres pg_dump -U rag_user rag_db > backup.sql

# 备份整个数据卷
tar -czvf data-backup.tar.gz data/volumes/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
