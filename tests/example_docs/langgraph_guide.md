# LangGraph 工作流框架

## 简介

LangGraph 是 LangChain 生态系统中的一个库，用于构建基于状态机的多代理工作流。它允许开发者通过图结构来定义复杂的 AI 应用流程。

## 核心概念

### 状态（State）
工作流的共享状态，在节点间传递。通常使用 TypedDict 定义：

```python
from typing import TypedDict

class WorkflowState(TypedDict):
    query: str
    context: str
    answer: str
    next_step: str
```

### 节点（Nodes）
图中的处理单元，接收状态、处理逻辑、返回更新后的状态：

```python
def process_node(state: WorkflowState) -> WorkflowState:
    # 处理逻辑
    state["answer"] = "处理结果"
    return state
```

### 边（Edges）
连接节点的路径，定义流程走向：

- **普通边**：固定走向
- **条件边**：根据状态决定走向

### 图构建

```python
from langgraph.graph import StateGraph, END

# 创建图
workflow = StateGraph(WorkflowState)

# 添加节点
workflow.add_node("node_a", process_a)
workflow.add_node("node_b", process_b)

# 设置入口
workflow.set_entry_point("node_a")

# 添加边
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# 编译
app = workflow.compile()

# 运行
result = app.invoke({"query": "测试"})
```

## 应用场景

### 1. RAG 流程
```
查询 -> 检索 -> 评分 -> (重写) -> 生成 -> 输出
```

### 2. 多代理协作
```
用户输入 -> 路由器 -> 代理A / 代理B / 代理C -> 汇总 -> 输出
```

### 3. 对话管理
```
用户输入 -> 意图识别 -> 知识检索 / 闲聊回复 -> 输出
```

## 高级特性

### 持久化
支持检查点和状态持久化，可恢复长时间运行的任务。

### 人机交互
支持在流程中暂停，等待人工输入后继续。

### 循环和条件
通过条件边实现复杂的循环逻辑：

```python
def should_continue(state):
    if state["iterations"] < 3:
        return "continue"
    return "end"

workflow.add_conditional_edges(
    "node_a",
    should_continue,
    {"continue": "node_b", "end": END}
)
```

## 优势

1. **可视化**：流程清晰，易于理解
2. **可调试**：每个节点的状态可检查
3. **可扩展**：容易添加新节点和分支
4. **状态管理**：自动处理状态传递

## 与其他框架对比

| 特性 | LangGraph | LangChain | LlamaIndex |
|------|-----------|-----------|------------|
| 流程定义 | 图结构 | 链式 | 工作流 |
| 循环支持 | 原生 | 需手动 | 有限 |
| 多代理 | 优秀 | 一般 | 一般 |
| 学习曲线 | 中等 | 低 | 低 |

LangGraph 适合需要复杂流程控制的场景，特别是需要循环、条件分支和多步骤决策的应用。
