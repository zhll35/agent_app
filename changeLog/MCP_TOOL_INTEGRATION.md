# 🔧 MCP 工具集成文档

## 📋 概述

本文档说明如何在 SOP 诊断流程中集成 MCP (Model Context Protocol) 工具，用于查询控制器配件信息。

---

## 🎯 功能说明

### step_2_match 步骤增强

在 `step_2_match`（核对控制器匹配性）步骤中，系统会自动调用 MCP 工具查询控制器与车型的兼容性。

**工作流程**：
1. 用户回答完第一步（电压）
2. 系统进入第二步（核对匹配性）
3. **自动调用 MCP 工具**查询兼容性
4. 根据查询结果返回相应的提示信息

---

## 🏗️ 架构设计

### 1. MCP 客户端 (`src/agent_app/tools/mcp_client.py`)

**核心类**：`MCPClient`

**主要方法**：
- `query_controller_compatibility()` - 查询控制器兼容性

**模式**：
- **模拟模式**（默认）：使用内置的模拟数据，用于开发和测试
- **真实模式**：连接到实际的 MCP 服务

**返回格式**：
```python
{
    "compatible": bool,      # 是否兼容（True/False/None）
    "confidence": float,     # 置信度 0-1
    "reason": str,          # 原因说明
    "alternative": str,     # 推荐的替代型号（可选）
    "details": dict         # 详细信息
}
```

### 2. 诊断 Agent 增强 (`src/agent_app/agents/executor.py`)

**新增方法**：
- `_execute_mcp_tool()` - 执行 MCP 工具调用

**工作流程**：
1. 检查步骤配置中是否有 `mcp_tool` 字段
2. 从状态中提取参数（车型、控制器型号等）
3. 调用 MCP 客户端
4. 根据结果生成响应消息

### 3. YAML 配置 (`src/agent_app/knowledge/templates/sop_diagnostic.yaml`)

**配置示例**：
```yaml
- id: step_2_match
  title: "核对控制器匹配性"
  action: "internal_lookup"
  prompt: "正在为您核对控制器与车型的匹配性，请稍候..."
  
  # MCP 工具调用配置
  mcp_tool:
    name: "query_controller_compatibility"
    description: "查询控制器与车型的兼容性"
    parameters:
      vehicle_model: "customer_info.vehicle_model"
      controller_model: "customer_info.controller_model"
      controller_brand: "customer_info.controller_brand"
  
  on_fail:
    message: "经核对，您手里的控制器版本与车型暂不匹配..."
  on_success:
    next: "step_3_wiring"
```

---

## 📊 数据流

```
用户回答第一步（电压）
    ↓
DiagnosticAgent.invoke()
    ↓
检测到下一步有 mcp_tool 配置
    ↓
_execute_mcp_tool()
    ↓
从 state.customer_info 提取参数
    ↓
MCPClient.query_controller_compatibility()
    ↓
返回兼容性结果
    ↓
根据结果生成响应消息
    ↓
返回给用户
```

---

## 🧪 测试

### 运行测试脚本

```bash
# 测试 MCP 客户端和诊断流程
python test_mcp_tool.py
```

### 测试用例

**用例 1：兼容的组合**
- 车型：九号 E100
- 控制器：Lingbo-72182
- 预期结果：✅ 兼容

**用例 2：不兼容的组合**
- 车型：九号 E100
- 控制器：Lingbo-72180
- 预期结果：❌ 不兼容，推荐 Lingbo-72182

**用例 3：未知的组合**
- 车型：未知车型
- 控制器：未知控制器
- 预期结果：⚠️ 未知，建议人工核对

---

## 🔄 完整交互示例

```
1️⃣ 用户: "我想调大电流"
   → Collector: "请提供车型、控制器型号..."

2️⃣ 用户: "九号 E100, Lingbo-72182"
   → Collector: "信息收集完整，开始排查..."
   → Diagnostician: "请确认全车电压是多少。"

3️⃣ 用户: "72V"
   → Diagnostician: 检测到下一步需要 MCP 工具
   → 调用 MCP: query_controller_compatibility(
       vehicle_model="九号 E100",
       controller_model="Lingbo-72182"
     )
   → MCP 返回: {"compatible": True, "reason": "完全匹配"}
   → 响应: "正在为您核对控制器与车型的匹配性，请稍候...
            
            ✅ 核对结果：该控制器型号与车型完全匹配，已在多个批次中验证"

4️⃣ 用户: "好的"
   → Diagnostician: "请拍一张转接线插头的照片..."
```

---

## 🔌 连接真实 MCP 服务

### 1. 配置环境变量

在 `.env` 文件中添加：
```bash
MCP_BASE_URL=http://your-mcp-service.com/api
```

### 2. 更新 settings.py

```python
class Settings(BaseSettings):
    # ... 其他配置 ...
    
    # MCP 服务配置
    MCP_BASE_URL: Optional[str] = None
```

### 3. 修改 MCP 客户端初始化

在 `src/agent_app/tools/mcp_client.py` 中：

```python
def get_mcp_client() -> MCPClient:
    """获取 MCP 客户端单例"""
    global _mcp_client
    if _mcp_client is None:
        from agent_app.settings import settings
        _mcp_client = MCPClient(base_url=settings.MCP_BASE_URL)
    return _mcp_client
```

---

## 📝 添加新的 MCP 工具

### 1. 在 MCPClient 中添加新方法

```python
def query_spare_parts(self, controller_model: str) -> Dict[str, Any]:
    """查询控制器配件信息"""
    # 实现查询逻辑
    pass
```

### 2. 在 executor.py 中添加处理逻辑

```python
def _execute_mcp_tool(self, step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
    tool_name = tool_config.get("name")
    
    if tool_name == "query_spare_parts":
        # 处理新工具
        result = self.mcp_client.query_spare_parts(...)
        return {"success": True, "data": result}
```

### 3. 在 YAML 中配置

```yaml
- id: step_spare_parts
  title: "查询配件信息"
  mcp_tool:
    name: "query_spare_parts"
    parameters:
      controller_model: "customer_info.controller_model"
```

---

## ✅ 优势

1. **自动化**：无需人工查询，自动核对兼容性
2. **准确性**：基于数据库的精确匹配
3. **可扩展**：易于添加新的 MCP 工具
4. **降级处理**：工具调用失败时自动降级
5. **模拟模式**：开发测试无需真实服务

---

## 🎉 总结

通过集成 MCP 工具，`step_2_match` 步骤现在可以：
- ✅ 自动查询控制器兼容性
- ✅ 提供详细的匹配结果
- ✅ 推荐替代型号（如果不兼容）
- ✅ 支持模拟和真实两种模式
- ✅ 优雅的错误处理和降级

**下一步**：可以继续添加更多 MCP 工具，如配件查询、库存查询等。

