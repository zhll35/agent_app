"""
Planner Agent - 电动车售后诊断规划器

注意：此模块当前未在主工作流中使用。
电动车售后诊断主要使用 DiagnosticAgent (executor.py) 执行 SOP 流程。
此文件保留用于未来可能的扩展需求。
"""
from __future__ import annotations
from typing import Any, Dict

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    规划 Agent（预留）

    当前电动车售后诊断使用固定的 SOP 流程（sop_diagnostic.yaml），
    不需要动态规划。此函数保留用于未来可能的复杂场景规划需求。
    """
    # 当前未实现，返回空规划
    return {
        "plan": {},
        "actions": [],
        "step": "planned"
    }
