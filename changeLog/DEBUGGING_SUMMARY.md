# 🎯 调试模式配置完成总结

## ✅ 已完成的配置

### 1. VSCode 调试配置
**文件**: `.vscode/launch.json`

提供了 4 个调试配置：
- ✅ **FastAPI Server (Debug)** - 后端调试 + 自动重载
- ✅ **FastAPI Server (No Reload)** - 后端调试（适合断点调试）
- ✅ **Python: Current File** - 调试当前打开的文件
- ✅ **Python: Test Graph Flow** - 调试图流程测试

**使用方法**: 按 **F5** 启动调试

---

### 2. 调试启动脚本
**文件**: `start_debug.sh`

**功能**:
- ✅ 自动设置 PYTHONPATH
- ✅ 启用 DEBUG 日志级别
- ✅ 检查 .env 配置
- ✅ 启动 uvicorn 服务器（带 reload）
- ✅ 显示详细的访问日志

**使用方法**:
```bash
./start_debug.sh
```

---

### 3. 增强的服务器日志
**文件**: `src/agent_app/runtime/server.py`

**新增功能**:
- ✅ 详细的请求日志（Thread ID, 消息内容, 客户信息）
- ✅ 执行过程追踪（开始/完成时间）
- ✅ 状态信息输出（is_info_complete, current_step, diagnostic_result）
- ✅ 消息类型和内容记录
- ✅ 完整的异常堆栈追踪

**日志示例**:
```
2024-01-11 18:30:15 - __main__ - INFO - 收到聊天请求 - Thread ID: abc-123
2024-01-11 18:30:15 - __main__ - DEBUG - 用户消息: 我想调大电流
2024-01-11 18:30:15 - __main__ - DEBUG - 客户信息: {
  "vehicle_model": "九号 E100",
  "controller_model": "Lingbo-72182",
  ...
}
2024-01-11 18:30:15 - __main__ - INFO - 开始执行 Agent Graph...
2024-01-11 18:30:16 - __main__ - INFO - Agent Graph 执行完成
2024-01-11 18:30:16 - __main__ - DEBUG - 执行结果状态:
2024-01-11 18:30:16 - __main__ - DEBUG -   - is_info_complete: True
2024-01-11 18:30:16 - __main__ - DEBUG -   - current_step: 0
2024-01-11 18:30:16 - __main__ - DEBUG -   - diagnostic_result: None
2024-01-11 18:30:16 - __main__ - DEBUG -   - 消息数量: 3
```

---

### 4. 完整的 README 文档
**文件**: `README.md`

**包含内容**:
- ✅ 快速开始指南
- ✅ 项目结构说明
- ✅ 4 种调试方法详解
- ✅ 常见问题解决方案
- ✅ 开发指南
- ✅ 部署说明

---

### 5. 调试快速指南
**文件**: `DEBUG_GUIDE.md`

**包含内容**:
- ✅ 快速启动命令
- ✅ VSCode 调试说明
- ✅ 常用调试命令
- ✅ 日志级别配置
- ✅ 组件单独调试方法
- ✅ 常见问题快速修复
- ✅ 性能分析工具
- ✅ 调试检查清单

---

## 🚀 如何开始调试

### 方式 1: 命令行调试（最简单）

```bash
# 1. 启动后端（调试模式）
./start_debug.sh

# 2. 在另一个终端启动前端
streamlit run src/agent_app/frontend/ui.py

# 3. 访问应用
# 前端: http://localhost:8501
# API文档: http://localhost:8000/docs
```

### 方式 2: VSCode 调试（最强大）

```bash
# 1. 打开 VSCode
# 2. 按 F5
# 3. 选择 "Python: FastAPI Server (Debug)"
# 4. 在代码中设置断点
# 5. 在另一个终端启动前端
streamlit run src/agent_app/frontend/ui.py
```

### 方式 3: 测试单个组件

```bash
# 测试图流程
PYTHONPATH=src python test_graph_flow.py

# 测试 API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test","thread_id":"123","mock_info":{}}'
```

---

## 📊 调试功能对比

| 功能 | 命令行调试 | VSCode 调试 | 组件测试 |
|------|-----------|------------|---------|
| 详细日志 | ✅ | ✅ | ✅ |
| 断点调试 | ❌ | ✅ | ✅ (pdb) |
| 变量查看 | ❌ | ✅ | ✅ (print) |
| 单步执行 | ❌ | ✅ | ✅ (pdb) |
| 自动重载 | ✅ | ✅ | ❌ |
| 调用栈 | ❌ | ✅ | ✅ (pdb) |
| 性能分析 | ⚠️ | ⚠️ | ✅ |

---

## 🔍 调试场景示例

### 场景 1: 调试信息收集流程

**问题**: 信息收集不完整时没有提示

**调试步骤**:
1. 在 `src/agent_app/agents/collector.py` 的 `check_missing_info` 函数设置断点
2. 启动 VSCode 调试器
3. 在前端发送消息
4. 查看 `missing_fields` 变量的值

### 场景 2: 调试诊断流程卡住

**问题**: 显示"信息收集完整，开始为您排查..."后没有后续

**调试步骤**:
1. 查看日志输出，确认是否进入 Diagnostician
2. 在 `src/agent_app/agents/executor.py` 的 `invoke` 方法设置断点
3. 检查 `current_step` 和 `steps` 的值
4. 确认消息是否正确返回

### 场景 3: 调试路由逻辑

**问题**: 不确定为什么路由到某个节点

**调试步骤**:
1. 在 `src/agent_app/graph/routing.py` 设置断点
2. 查看 `state` 的值
3. 单步执行，观察路由决策过程

---

## 📝 调试最佳实践

### 1. 使用分层日志

```python
logger.debug("详细的调试信息")  # 开发时使用
logger.info("重要的业务信息")   # 生产环境保留
logger.warning("警告信息")      # 需要注意的问题
logger.error("错误信息")        # 错误和异常
```

### 2. 添加上下文信息

```python
logger.info(f"处理请求 - Thread: {thread_id}, User: {user_id}")
```

### 3. 使用结构化日志

```python
logger.debug(f"状态变化: {json.dumps(state, ensure_ascii=False, indent=2)}")
```

### 4. 异常处理

```python
try:
    # 你的代码
except Exception as e:
    logger.error(f"处理失败: {str(e)}", exc_info=True)  # exc_info=True 会输出堆栈
    raise
```

---

## 🎓 学习资源

### 调试技巧
- [Python 官方调试文档](https://docs.python.org/3/library/pdb.html)
- [VSCode Python 调试](https://code.visualstudio.com/docs/python/debugging)
- [FastAPI 调试指南](https://fastapi.tiangolo.com/tutorial/debugging/)

### LangGraph 调试
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangSmith 追踪](https://docs.smith.langchain.com/)

---

## ✨ 下一步

1. **熟悉调试工具**: 尝试不同的调试方法
2. **设置断点**: 在关键位置设置断点，观察执行流程
3. **查看日志**: 理解每个步骤的日志输出
4. **测试场景**: 使用 `test_graph_flow.py` 测试不同场景
5. **优化代码**: 根据调试结果优化代码

---

## 📞 需要帮助？

- 查看 `README.md` 获取完整文档
- 查看 `DEBUG_GUIDE.md` 获取快速参考
- 运行 `./start_debug.sh` 启动调试模式
- 访问 http://localhost:8000/docs 查看 API 文档

---

**祝调试顺利！🎉**

