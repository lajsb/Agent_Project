# Docker 配置指南

本指南帮助您配置 Docker 来运行 Milvus 向量数据库。

## 前置要求

1. **安装 Docker Desktop**
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/desktop/install/linux-install/

2. **确认 Docker 安装成功**
   ```bash
   docker --version
   docker-compose --version
   ```

## 项目 Docker 配置

本项目包含 `docker-compose.yml` 文件，用于启动 Milvus 向量数据库。

### 服务组成

| 服务 | 端口 | 说明 |
|------|------|------|
| etcd | 2379 | 元数据存储 |
| minio | 9000, 9001 | 对象存储 |
| milvus | 19530 | 向量数据库 |

### 启动 Milvus

```bash
# 在项目根目录执行
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f milvus
```

### 停止 Milvus

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 仅重启 milvus
docker-compose restart milvus
```

## 常见问题

### 1. Docker Desktop 无法启动

**Windows 用户:**
- 确保已启用 WSL2: `wsl --install`
- 在 Docker Desktop 设置中启用 WSL2 集成
- 检查虚拟化是否已在 BIOS 中启用

**解决步骤:**
```powershell
# 检查 WSL 状态
wsl --status

# 更新 WSL
wsl --update

# 设置默认 WSL 版本为 2
wsl --set-default-version 2
```

### 2. 端口冲突

如果 19530 端口被占用，修改 `docker-compose.yml`:

```yaml
ports:
  - "19531:19530"  # 改为其他端口
```

同时修改项目 `.env` 文件:
```env
MILVUS_PORT=19531
```

### 3. 内存不足

Milvus 需要至少 4GB 内存。在 Docker Desktop 设置中调整:
- Settings -> Resources -> Memory: 建议 8GB

### 4. 数据持久化

数据存储在项目目录的 `volumes/` 文件夹中:
- `volumes/etcd/` - etcd 数据
- `volumes/minio/` - minio 数据
- `volumes/milvus/` - milvus 数据

删除这些文件夹会清除所有数据。

## 验证 Milvus 连接

启动后，验证 Milvus 是否正常运行:

```bash
# 使用 Python 验证
python -c "
from pymilvus import connections, utility
connections.connect(host='localhost', port='19530')
print('Collections:', utility.list_collections())
print('Milvus 连接成功!')
"
```

## 完整启动流程

```bash
# 1. 启动 Docker Desktop
# 在开始菜单中找到 Docker Desktop 并启动

# 2. 等待 Docker 完全启动
# 看到 Docker Desktop 界面显示 "Engine running"

# 3. 在项目目录启动 Milvus
cd D:\codevs\rag_plus
docker-compose up -d

# 4. 等待约 30 秒让服务完全启动
docker-compose ps

# 5. 启动后端服务
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 6. 启动前端服务（新开终端）
cd frontend
npm run dev
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Milvus | localhost:19530 | 向量数据库 |
| Minio 控制台 | http://localhost:9001 | 对象存储管理界面 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| 前端 | http://localhost:5173 | React 应用 |
| API 文档 | http://localhost:8000/docs | Swagger UI |

## 故障排除

### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务
docker-compose logs milvus
docker-compose logs etcd
docker-compose logs minio

# 实时跟踪日志
docker-compose logs -f milvus
```

### 重置所有数据

```bash
# 停止服务
docker-compose down

# 删除数据卷
rm -rf volumes/

# 重新启动
docker-compose up -d
```

### 更新 Milvus 版本

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

## 参考文档

- [Milvus Docker 安装指南](https://milvus.io/docs/install_standalone-docker.md)
- [Docker Compose 文档](https://docs.docker.com/compose/)
