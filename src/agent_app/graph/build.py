from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agent_app.graph.state import AgentState
from agent_app.graph.constants import *
from agent_app.graph.routing import route_supervisor, route_after_collector

# 导入具体的 Agent 函数
from agent_app.agents.executor import diagnostic_agent
from agent_app.agents.collector import collector_node

def build_graph():
    """构建 LangGraph 工作流"""
    workflow = StateGraph(AgentState)

    # 1. 添加节点
    workflow.add_node(NODE_COLLECTOR, collector_node)
    workflow.add_node(NODE_DIAGNOSTICIAN, diagnostic_agent.invoke)

    # 2. 设置条件入口点（使用 Supervisor 路由逻辑）
    # 注意：使用 set_conditional_entry_point 时不需要 set_entry_point
    workflow.set_conditional_entry_point(
        route_supervisor,
        {
            NODE_COLLECTOR: NODE_COLLECTOR,
            NODE_DIAGNOSTICIAN: NODE_DIAGNOSTICIAN,
            "__end__": END
        }
    )

    # 3. 设置边 (Edge)
    # Collector 完成后，根据信息是否完整决定下一步
    workflow.add_conditional_edges(
        NODE_COLLECTOR,
        route_after_collector,
        {
            NODE_DIAGNOSTICIAN: NODE_DIAGNOSTICIAN,
            "__end__": END
        }
    )

    # Diagnostician 完成后，检查是否结束
    from agent_app.graph.routing import route_after_diagnostician
    workflow.add_conditional_edges(
        NODE_DIAGNOSTICIAN,
        route_after_diagnostician,
        {
            "__end__": END
        }
    )

    # 4. 编译（添加 Checkpoint 以保存状态）
    # 使用内存 Checkpoint，生产环境可以换成 SqliteSaver 或 RedisSaver
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app