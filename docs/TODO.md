# RAG Agent 项目开发计划书

> 版本: 1.0  
> 日期: 2026-04-08  
> 状态: 规划阶段

---

## 一、项目概述

### 1.1 项目目标
开发一个基于 RAG (Retrieval-Augmented Generation) 技术的智能知识库问答系统，支持文档上传、向量检索和多轮对话。

### 1.2 核心功能
- 📚 文档上传与处理（PDF/DOCX/TXT/Markdown）
- 🔍 智能检索（向量相似度 + 重排序）
- 💬 多轮对话（支持会话隔离和历史记录）
- 🤖 Agent 能力（自适应 RAG 策略：Step-back + HyDE）
- 🎨 Web 界面（响应式设计，苹果风格）

### 1.3 技术栈

**后端**
- 语言: Python 3.12+
- 框架: FastAPI + Uvicorn
- AI: LangChain + LangGraph + OpenAI API
- 向量数据库: Milvus 2.3+
- 关系数据库: PostgreSQL 15+
- 缓存: Redis (可选)
- 包管理: uv

**前端**
- 框架: React 18 + TypeScript
- 构建: Vite
- 样式: Tailwind CSS
- 图标: Lucide React

**基础设施**
- 容器化: Docker + Docker Compose
- 反向代理: Nginx (生产环境)
- 监控: Prometheus + Grafana (可选)

---

## 二、项目阶段划分

### 阶段 0: 前期准备 (Week 1)
### 阶段 1: 基础设施搭建 (Week 1-2)
### 阶段 2: 后端核心开发 (Week 2-5)
### 阶段 3: 前端开发 (Week 4-6)
### 阶段 4: 集成测试 (Week 6-7)
### 阶段 5: 部署优化 (Week 7-8)

---

## 三、详细任务清单

## 阶段 0: 前期准备

### Week 1, Day 1-2: 需求分析
- [ ] **0.1.1** 编写产品需求文档 (PRD)
  - 用户故事梳理
  - 功能优先级划分 (MoSCoW)
  - 非功能性需求 (性能/安全/可用性)
- [ ] **0.1.2** 竞品分析
  - 调研类似产品 (ChatGPT with files, Claude Projects)
  - 确定差异化功能
- [ ] **0.1.3** 用户流程设计
  - 绘制用户旅程地图
  - 确定核心使用场景

### Week 1, Day 3-4: 技术选型与架构设计
- [ ] **0.2.1** 技术选型报告
  - 对比向量数据库 (Milvus vs Pinecone vs Weaviate)
  - 对比 LLM 提供商 (OpenAI vs Anthropic vs 国产)
  - 对比前端框架 (React vs Vue)
- [ ] **0.2.2** 系统架构设计
  - 绘制架构图 (C4 Model: Level 1-3)
  - 数据流设计
  - API 设计规范 (RESTful + OpenAPI)
- [ ] **0.2.3** 数据库设计
  - ER 图设计
  - 表结构设计
  - 索引策略规划

### Week 1, Day 5: 开发规范制定
- [ ] **0.3.1** 代码规范
  - Python: PEP 8 + Black + Ruff + MyPy
  - TypeScript: ESLint + Prettier
  - Git 分支策略 (Git Flow / GitHub Flow)
- [ ] **0.3.2** 文档模板
  - README 模板
  - API 文档模板
  - 提交信息规范 (Conventional Commits)
- [ ] **0.3.3** 项目管理工具配置
  - GitHub Projects / Jira 设置
  - CI/CD 流程设计

---

## 阶段 1: 基础设施搭建

### Week 1, Day 5 - Week 2, Day 2: 开发环境搭建
- [ ] **1.1.1** 项目初始化
  - 创建 Git 仓库
  - 设置 .gitignore (Python + Node + Docker)
  - 选择并配置开源许可证 (MIT/Apache)
- [ ] **1.1.2** Python 环境配置
  - 安装 uv 包管理器
  - 创建 pyproject.toml
  - 配置开发依赖 (black, ruff, mypy, pytest)
  - 生成初始 uv.lock
- [ ] **1.1.3** Node.js 环境配置
  - 初始化 frontend 目录
  - 配置 package.json
  - 安装 Vite + React + TypeScript
  - 配置 ESLint + Prettier
- [ ] **1.1.4** Docker 环境配置
  - 创建 Dockerfile (多阶段构建)
  - 创建 docker-compose.yml (开发环境)
  - 创建 docker-compose.prod.yml (生产环境)
  - 配置 .dockerignore

### Week 2, Day 3-4: CI/CD 与工具链
- [ ] **1.2.1** GitHub Actions 配置
  - Python 代码检查 (lint + type check)
  - 前端构建检查
  - Docker 镜像构建
  - 自动化测试
- [ ] **1.2.2** 预提交钩子 (pre-commit)
  - 配置 .pre-commit-config.yaml
  - 集成 black, ruff, mypy
  - 前端代码格式化检查
- [ ] **1.2.3** 文档站点初始化
  - 配置 MkDocs / Docusaurus
  - 创建基础文档结构

### Week 2, Day 5: 基础设施测试
- [ ] **1.3.1** 本地开发环境验证
  - Docker Compose 启动测试
  - 热重载功能测试
  - 端口映射检查
- [ ] **1.3.2** CI 流程测试
  - 提交测试代码触发 CI
  - 验证所有检查通过
- [ ] **1.3.3** 文档发布测试
  - 验证文档站点可访问

---

## 阶段 2: 后端核心开发

### Week 2, Day 5 - Week 3, Day 3: 数据库层 (Data Layer)
- [ ] **2.1.1** 数据库连接模块
  - 实现数据库连接池 (SQLAlchemy + asyncpg)
  - 配置数据库迁移 (Alembic)
  - 连接健康检查
- [ ] **2.1.2** ORM 模型定义
  - 基础模型 (Base Model)
  - AgentMemory 模型 (对话历史)
  - User 模型 (用户管理)
  - Document 模型 (文档元数据)
  - 所有模型添加索引优化
- [ ] **2.1.3** Repository 层
  - BaseRepository (CRUD 封装)
  - MemoryRepository (对话历史查询)
  - UserRepository (用户查询)
  - 实现分页和排序功能
- [ ] **2.1.4** Service 层
  - MemoryService (对话历史业务逻辑)
  - UserService (用户管理)
  - 事务管理实现
- [ ] **2.1.5** 数据库测试
  - 单元测试 (pytest)
  - 集成测试
  - 性能测试 (大量数据插入)

### Week 3, Day 4 - Week 4, Day 2: 向量数据库层
- [ ] **2.2.1** Milvus 客户端封装
  - 连接管理
  - 集合管理 (创建/删除/查询)
  - 向量插入和检索
- [ ] **2.2.2** Embedding 服务
  - DashScope Embedding 封装
  - 批量 embedding 优化
  - 错误重试机制
- [ ] **2.2.3** 文档分块策略
  - 递归字符分块
  - Markdown 分块 (按标题)
  - 代码分块
  - 分块重叠策略
- [ ] **2.2.4** 文档处理管道
  - 文档加载器 (PDF/DOCX/TXT)
  - 文档解析器
  - 清洗和预处理
  - 元数据提取
- [ ] **2.2.5** 向量存储测试
  - 插入性能测试
  - 检索准确性测试
  - 大规模数据测试 (10k+ 文档)

### Week 4, Day 3 - Week 5, Day 2: RAG 核心引擎
- [ ] **2.3.1** 检索模块
  - 向量相似度检索
  - 关键词检索 (BM25)
  - 混合检索策略
  - 重排序 (Rerank)
- [ ] **2.3.2** RAG Graph (LangGraph)
  - 状态定义 (RAGState)
  - 节点实现:
    - retrieve: 文档检索
    - grade_documents: 文档评分
    - rewrite_query: 查询重写
    - generate: 答案生成
  - 边逻辑:
    - 相关性判断
    - 路由决策
- [ ] **2.3.3** 查询重写策略
  - Step-back: 退一步思考
  - HyDE: 假设文档生成
  - Complex: 组合策略
- [ ] **2.3.4** Prompt 工程
  - 系统 Prompt 设计
  - RAG Prompt 模板
  - Few-shot 示例
  - Prompt 版本管理
- [ ] **2.3.5** RAG 测试
  - 单元测试 (每个节点)
  - 端到端测试
  - 效果评估 (准确率/召回率)

### Week 5, Day 3-5: Agent 与对话管理
- [ ] **2.4.1** Agent 核心
  - ReAct Agent 实现
  - 工具定义:
    - rag_tool: RAG 检索
    - calculator: 计算器
    - weather: 天气查询 (可选)
  - 工具调用逻辑
- [ ] **2.4.2** 对话历史管理
  - 历史记录持久化
  - 上下文窗口管理
  - 会话隔离
  - 多轮对话优化
- [ ] **2.4.3** 对话服务
  - 对话接口
  - 流式响应 (SSE)
  - 错误处理
  - 限流和熔断
- [ ] **2.4.4** Agent 测试
  - 工具调用测试
  - 对话流程测试
  - 边界情况处理

---

## 阶段 3: API 层与前端开发

### Week 4, Day 3 - Week 5, Day 5: API 开发 (与 RAG 并行)
- [ ] **3.1.1** FastAPI 应用框架
  - 应用初始化
  - 中间件配置 (CORS/日志/异常处理)
  - 生命周期管理
- [ ] **3.1.2** Pydantic 模型
  - Request/Response 模型
  - 字段验证
  - 示例数据
- [ ] **3.1.3** API 路由实现
  - `/chat` 对话接口
  - `/chat/history` 历史记录
  - `/chat/conversations` 会话列表
  - `/documents/upload` 文档上传
  - `/documents/stats` 统计信息
  - `/health` 健康检查
- [ ] **3.1.4** 认证与授权
  - JWT 认证
  - API Key 支持
  - 权限控制 (RBAC)
- [ ] **3.1.5** API 测试
  - 单元测试 (pytest)
  - 集成测试
  - 负载测试 (locust)

### Week 5, Day 1 - Week 6, Day 3: 前端界面开发
- [ ] **3.2.1** 项目初始化
  - Vite + React + TS 配置
  - Tailwind CSS 配置 (苹果风格)
  - 路由配置 (React Router)
  - 状态管理 (Zustand/Context)
- [ ] **3.2.2** UI 组件库
  - 基础组件: Button, Input, Card, Modal
  - 消息组件: MessageBubble, MessageList
  - 布局组件: Sidebar, Header, Layout
  - 加载组件: Skeleton, Spinner
- [ ] **3.2.3** 页面实现
  - 登录页面
  - 对话页面 (ChatPage)
  - 文档管理页面 (DocumentsPage)
  - 历史记录页面 (HistoryPage)
- [ ] **3.2.4** API 集成
  - Axios 配置
  - API Client 封装
  - 错误处理
  - 请求拦截器
- [ ] **3.2.5** 交互优化
  - 消息自动滚动
  - 输入框快捷键
  - 文件拖拽上传
  - 响应式适配

### Week 6, Day 4-5: 前端优化与测试
- [ ] **3.3.1** 性能优化
  - 组件懒加载
  - 虚拟滚动 (长对话)
  - 图片/文件懒加载
  - 缓存策略
- [ ] **3.3.2** 前端测试
  - 单元测试 (Vitest)
  - 组件测试 (Storybook)
  - E2E 测试 (Playwright)
- [ ] **3.3.3** 构建优化
  - 分包策略
  - Tree shaking
  - Gzip/Brotli 压缩
  - CDN 配置

---

## 阶段 4: 集成测试与优化

### Week 6, Day 5 - Week 7, Day 3: 端到端测试
- [ ] **4.1.1** 集成测试
  - 完整对话流程测试
  - 文档上传流程测试
  - 多用户并发测试
- [ ] **4.1.2** 性能测试
  - 接口响应时间测试
  - 并发用户测试 (100/500/1000)
  - 数据库性能测试
  - 向量检索性能测试
- [ ] **4.1.3** 安全测试
  - SQL 注入测试
  - XSS 防护测试
  - CSRF 防护测试
  - 敏感信息泄露检查
- [ ] **4.1.4** 用户体验测试
  - 可用性测试
  - 响应式测试 (移动端/平板/桌面)
  - 浏览器兼容性测试

### Week 7, Day 4-5: Bug 修复与优化
- [ ] **4.2.1** 问题修复
  - Bug 分类和优先级
  - 修复并验证
  - 回归测试
- [ ] **4.2.2** 性能优化
  - 数据库查询优化
  - 缓存策略优化
  - 前端渲染优化
- [ ] **4.2.3** 日志与监控
  - 结构化日志 (JSON)
  - 错误追踪 (Sentry)
  - 性能监控 (APM)
  - 业务指标监控

---

## 阶段 5: 部署与交付

### Week 7, Day 5 - Week 8, Day 3: 生产环境部署
- [ ] **5.1.1** 基础设施准备
  - 云服务器选型 (AWS/阿里云/GCP)
  - 域名和 SSL 证书
  - 网络配置 (VPC/安全组)
- [ ] **5.1.2** 容器编排
  - Kubernetes 配置 (可选)
  - Docker Swarm 配置
  - 服务发现配置
- [ ] **5.1.3** 数据库部署
  - PostgreSQL 生产配置
  - Milvus 集群配置
  - Redis 集群配置
  - 备份策略
- [ ] **5.1.4** 应用部署
  - 后端服务部署
  - 前端静态资源部署 (CDN)
  - Nginx 反向代理配置
  - 负载均衡配置
- [ ] **5.1.5** 持续部署
  - CD 流水线配置
  - 蓝绿部署/金丝雀发布
  - 回滚策略

### Week 8, Day 4-5: 文档与交付
- [ ] **5.2.1** 用户文档
  - 快速开始指南
  - 功能使用手册
  - 常见问题 FAQ
  - 视频教程
- [ ] **5.2.2** 开发文档
  - API 文档 (Swagger/OpenAPI)
  - 架构设计文档
  - 部署运维手册
  - 开发贡献指南
- [ ] **5.2.3** 项目交付
  - 代码最终审查
  - 交付清单确认
  - 知识转移
  - 维护计划

---

## 四、风险管理

### 高风险项
| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| LLM API 不稳定 | 高 | 实现重试机制 + 降级策略 |
| 大文件处理超时 | 中 | 异步任务队列 (Celery) |
| 向量检索性能差 | 高 | 索引优化 + 缓存 |
| 浏览器兼容性 | 中 | 渐进增强 + Polyfill |

### 技术债务跟踪
- [ ] 文档分块算法优化
- [ ] 对话历史压缩存储
- [ ] 图片/表格解析支持
- [ ] 多语言支持

---

## 五、里程碑与检查点

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M0: 基础设施完成 | Week 2 | CI/CD + Docker |
| M1: 数据库层完成 | Week 3 | 模型 + Repository |
| M2: RAG 核心完成 | Week 5 | 检索 + 生成 |
| M3: API 完成 | Week 5 | FastAPI + 文档 |
| M4: 前端完成 | Week 6 | React 界面 |
| M5: 测试完成 | Week 7 | 测试报告 |
| M6: 生产上线 | Week 8 | 部署完成 |

---

## 六、资源需求

### 人力资源
- 后端工程师: 1-2 人
- 前端工程师: 1 人
- DevOps 工程师: 0.5 人 (兼职)
- 产品经理: 0.5 人 (兼职)

### 基础设施
- 开发环境: Docker Desktop
- 测试环境: 云服务器 2C4G
- 生产环境: 云服务器 4C8G+
- 监控: Prometheus + Grafana

---

## 七、附录

### A. 技术栈版本锁定
- Python: 3.12
- Node.js: 18 LTS
- PostgreSQL: 15
- Milvus: 2.3
- React: 18

### B. 参考资源
- [LangChain 文档](https://python.langchain.com/)
- [Milvus 文档](https://milvus.io/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)

### C. 项目模板
- 后端结构参考: [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- 前端结构参考: [Bulletproof React](https://github.com/alan2207/bulletproof-react)

---

**文档维护历史**
- v1.0 (2026-04-08): 初始版本

**审阅人**
- [ ] 技术负责人
- [ ] 产品经理
- [ ] 开发团队
