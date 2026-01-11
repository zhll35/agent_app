from typing import Dict, List
from agent_app.graph.state import AgentState

def check_missing_info(info: Dict) -> List[str]:
    """[cite: 10-30] 检查核心字段缺失"""
    missing = []
    
    # 基础信息
    if not info.get("controller_model"):
        missing.append("控制器型号（智科请拍钢印，凌博请截图小程序）")
    if not info.get("vehicle_model"):
        missing.append("车辆具体型号")
        
    # 电机
    if not info.get("motor_power"):
        missing.append("电机功率及尺寸")
        
    # 电池强校验 [cite: 26]
    if not info.get("battery_type"):
        missing.append("电池类型（铅酸或锂电）")
    elif info.get("battery_type") == "lithium" and not info.get("bms_current"):
        missing.append("锂电池保护板持续电流（非常重要！）")
        
    return missing

def collector_node(state: AgentState) -> Dict:
    """Collector Agent 的简单实现"""
    info = state.get("customer_info", {})
    missing_fields = check_missing_info(info)

    if missing_fields:
        # [cite: 32] 像检查清单一样礼貌追问
        prompt = "为了精准调试，还需要麻烦您补充以下信息：\n" + "\n".join([f"- {f}" for f in missing_fields])
        return {
            "messages": [("assistant", prompt)],
            "is_info_complete": False
        }
    else:
        return {
            "messages": [("assistant", "信息收集完整，开始为您排查...")],
            "is_info_complete": True
        }