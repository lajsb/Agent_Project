# RAG Agent 项目运行指南

本文档介绍如何运行 RAG Agent 项目。

## 目录结构

```
rag_plus/                    <-- 项目根目录（在这里启动）
├── backend/                 # 后端代码
│   ├── api/                 # FastAPI API
│   │   ├── main.py         # 后端入口文件
│   │   └── routes/         # API路由
│   ├── db/                  # 数据库模型和服务
│   ├── milvus/              # Milvus 客户端
│   └── src/                 # 核心业务逻辑
├── frontend/                # React 前端
├── scripts/                 # 启动脚本
│   └── run_api.py          # 后端启动脚本
├── tests/                   # 测试文件
├── docker/                  # Docker 配置
│   └── docker-compose.yml  # Docker服务配置
└── data/                    # 数据卷 (Docker 数据)
```

## 前置要求

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Git

## 环境配置

### 1. 进入项目目录

```bash
cd D:\codevs\rag_plus
```

### 2. 创建 .env 文件

```bash
# Windows PowerShell
copy .env.example .env

# 或 Linux/Mac
cp .env.example .env
```

### 3. 编辑 .env 文件

用文本编辑器打开 `.env`，填入你的 API 密钥：

```env
# ===== LLM 配置 (Moonshot) =====
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=kimi-k2-0905-preview

# ===== Embedding 模型配置 (DashScope) =====
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_API_KEY=your_dashscope_key_here
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ===== 数据库配置 (PostgreSQL) =====
DATABASE_URL=postgresql://rag_user:rag_password@localhost:5432/rag_db

# ===== Milvus 配置 =====
MILVUS_HOST=127.0.0.1
MILVUS_PORT=19530
```

## 启动步骤

### 第一步：启动数据库服务

**必须在项目根目录执行！**

```bash
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml up -d
```

等待 30-60 秒，检查容器状态：

```bash
docker ps
```

应该看到 4 个容器在运行：
- `rag-postgres` (PostgreSQL)
- `milvus-standalone` (Milvus)
- `milvus-minio` (MinIO)
- `milvus-etcd` (Etcd)

### 第二步：安装依赖（使用 uv）

本项目使用 [uv](https://docs.astral.sh/uv/) 进行 Python 依赖管理。

#### 安装 uv（如果尚未安装）

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 安装项目依赖

```bash
cd D:\codevs\rag_plus

# 使用 uv 安装依赖（根据 uv.lock 文件）
uv sync

# 或者使用 uv 运行（无需手动安装到系统环境）
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 常用 uv 命令

```bash
# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 更新依赖并重新生成 uv.lock
uv lock

# 运行 Python 脚本
uv run python scripts/ingest.py

# 进入项目的虚拟环境 shell
uv shell
```

### 第三步：启动后端（关键步骤）

**⚠️ 非常重要：必须在项目根目录启动，不要在 backend 目录启动！**

```bash
cd D:\codevs\rag_plus

# 方式一：使用 uv 运行（推荐）
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# 方式二：使用启动脚本
cd scripts
uv run python run_api.py --reload

# 方式三：如果已激活虚拟环境
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**正确的目录：**
```
D:\codevs\rag_plus> uvicorn backend.api.main:app --reload
```

**错误的目录（会报错）：**
```
D:\codevs\rag_plus\backend> uvicorn api.main:app --reload  ❌
```

成功启动后：
- API 地址: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 第四步：启动前端

**新开一个终端窗口：**

```bash
cd D:\codevs\rag_plus\frontend

# 安装依赖（首次运行需要）
npm install

# 启动开发服务器
npm run dev
```

成功启动后：
- 前端地址: http://localhost:5173

## 完整启动流程示例

```bash
# 终端 1：启动数据库
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml up -d

# 等待 30 秒...

# 终端 1：启动后端（使用 uv）
cd D:\codevs\rag_plus
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2：启动前端
cd D:\codevs\rag_plus\frontend
npm install
npm run dev
```

## 验证运行

### 1. 检查后端 API

打开浏览器访问：http://localhost:8000/health

应该返回：
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "milvus": "connected"
  }
}
```

### 2. 检查前端

打开浏览器访问：http://localhost:5173

应该能看到登录页面。

### 3. 运行测试

```bash
cd D:\codevs\rag_plus

# 使用 uv 运行测试
uv run python tests/test_postgres.py

# 或者直接使用 Python（如果已激活虚拟环境）
python tests/test_postgres.py
```

## 常用命令

### 数据库管理

```bash
# 查看容器状态
docker-compose -f docker/docker-compose.yml ps

# 查看 PostgreSQL 日志
docker-compose -f docker/docker-compose.yml logs postgres

# 进入 PostgreSQL 容器
docker-compose -f docker/docker-compose.yml exec postgres psql -U rag_user -d rag_db

# 重启数据库
docker-compose -f docker/docker-compose.yml restart

# 停止所有服务
docker-compose -f docker/docker-compose.yml down
```

### 文档导入

```bash
# 导入单个文件（使用 uv）
cd D:\codevs\rag_plus
uv run python scripts/ingest.py --file path/to/document.pdf

# 导入整个目录
uv run python scripts/ingest.py --dir path/to/documents/

# 查看知识库统计
uv run python scripts/ingest.py --stats

# 如果已激活虚拟环境，可以直接使用 python
python scripts/ingest.py --file path/to/document.pdf
```

## 故障排除

### ❌ 错误：ModuleNotFoundError: No module named 'backend'

**原因**：在错误的目录启动了服务

**错误示例**：
```bash
cd D:\codevs\rag_plus\backend
uvicorn api.main:app --reload  ❌ 错误！
```

**正确做法**：
```bash
cd D:\codevs\rag_plus
uvicorn backend.api.main:app --reload  ✅ 正确！
```

### ❌ 错误：数据库连接失败

**原因**：PostgreSQL 容器未启动

**解决**：
```bash
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml up -d postgres
docker-compose -f docker/docker-compose.yml logs postgres
```

### ❌ 错误：Milvus 连接失败

**原因**：Milvus 容器未启动或正在初始化

**解决**：
```bash
# 等待 60 秒后重试
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml ps
docker-compose -f docker/docker-compose.yml logs milvus
```

### ❌ 错误：前端无法连接后端

**原因**：后端未启动或端口冲突

**解决**：
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查端口占用
netstat -ano | findstr 8000
```

## 数据备份

```bash
# 备份 PostgreSQL 数据库
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml exec -T postgres pg_dump -U rag_user rag_db > backup.sql

# 备份整个数据卷
tar -czvf data-backup.tar.gz data/volumes/
```

## 停止服务

```bash
# 停止后端 (在运行后端的终端按 Ctrl+C)

# 停止前端 (在运行前端的终端按 Ctrl+C)

# 停止数据库
cd D:\codevs\rag_plus
docker-compose -f docker/docker-compose.yml down
```

## 访问地址汇总

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:5173 | React 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | 数据库 |
| Milvus | localhost:19530 | 向量数据库 |

## 注意事项

1. **⚠️ 必须在项目根目录启动后端**，不要在 backend 目录启动
2. 首次启动 Docker 服务需要下载镜像，请耐心等待
3. 所有数据存储在 `data/volumes/` 目录，请勿删除
4. 修改代码后后端会自动重载（`--reload` 模式）
5. 项目使用 **uv** 管理 Python 依赖，不要手动使用 pip 安装依赖

## 依赖管理（uv）

本项目使用 [uv](https://docs.astral.sh/uv/) 进行 Python 依赖管理，相比传统的 `requirements.txt`，uv 具有以下优势：

- **快速**：使用 Rust 编写，比 pip 快 10-100 倍
- **可靠**：通过 `uv.lock` 文件锁定依赖版本，确保环境一致
- **方便**：自动管理虚拟环境，无需手动激活

### 项目依赖文件

- `pyproject.toml` - 项目配置和依赖声明
- `uv.lock` - 锁定的依赖版本（自动生成，不要手动修改）

### 常用命令

```bash
# 安装所有依赖（根据 uv.lock）
uv sync

# 添加新依赖
uv add requests

# 添加开发依赖
uv add --dev pytest

# 更新依赖
uv lock

# 运行命令（自动使用项目虚拟环境）
uv run python script.py

# 进入虚拟环境 shell
uv shell
```

## 下一步

启动成功后，你可以：
1. 打开 http://localhost:5173 访问前端
2. 注册/登录账号
3. 上传文档到知识库
4. 开始智能对话
