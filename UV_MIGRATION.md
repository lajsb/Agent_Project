# 迁移到 uv 依赖管理

本项目已从传统的 `requirements.txt` 迁移到使用 [uv](https://docs.astral.sh/uv/) 进行 Python 依赖管理。

## 主要变化

### 1. 依赖声明文件

- **旧方式**: `requirements.txt`
- **新方式**: `pyproject.toml` + `uv.lock`

### 2. 安装依赖

**旧方式:**
```bash
pip install -r requirements.txt
```

**新方式:**
```bash
uv sync
# 或者
uv run <command>
```

### 3. 运行后端

**旧方式:**
```bash
uvicorn backend.api.main:app --reload
```

**新方式:**
```bash
uv run uvicorn backend.api.main:app --reload
```

## 文件说明

| 文件 | 用途 | 是否需手动编辑 |
|------|------|---------------|
| `pyproject.toml` | 项目配置和依赖声明 | 是 |
| `uv.lock` | 锁定的依赖版本 | 否（自动生成） |

## 安装 uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 快速开始

```bash
# 1. 进入项目目录
cd D:\codevs\rag_plus

# 2. 安装依赖
uv sync

# 3. 启动后端
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 为什么使用 uv？

1. **速度快**: 比 pip 快 10-100 倍
2. **可靠**: 锁文件确保所有开发者使用相同的依赖版本
3. **方便**: 自动管理虚拟环境，无需手动激活
4. **现代**: 支持 PEP 621 标准

## 更多信息

- [uv 官方文档](https://docs.astral.sh/uv/)
- [项目运行指南](./docs/run.md)
