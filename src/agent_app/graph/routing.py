from typing import Literal
from agent_app.graph.state import AgentState
from agent_app.graph.constants import *

def route_supervisor(state: AgentState) -> Literal[NODE_COLLECTOR, NODE_DIAGNOSTICIAN, "__end__"]:
    """主路由逻辑"""

    # 1. 检查信息是否完整
    if not state.get("is_info_complete"):
        return NODE_COLLECTOR

    # 2. 检查是否有诊断结果
    if state.get("diagnostic_result"):
        return "__end__"

    # 3. 默认进入诊断
    return NODE_DIAGNOSTICIAN

def route_after_collector(state: AgentState) -> Literal[NODE_DIAGNOSTICIAN, "__end__"]:
    """Collector 节点完成后的路由逻辑"""

    # 如果信息收集完整，进入诊断流程
    if state.get("is_info_complete"):
        return NODE_DIAGNOSTICIAN

    # 否则结束，等待用户补充信息
    return "__end__"

def route_after_diagnostician(state: AgentState) -> Literal["__end__"]:
    """Diagnostician 节点完成后的路由逻辑"""

    # 诊断流程总是结束，等待用户下一次输入
    # 状态会被保存在 checkpoint 中，下次继续
    return "__end__"