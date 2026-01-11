#!/usr/bin/env python3
"""
测试 MCP 工具调用功能
"""

import sys
sys.path.insert(0, 'src')

from agent_app.tools import get_mcp_client
import json


def test_mcp_client():
    """测试 MCP 客户端"""
    print("=" * 60)
    print("测试 MCP 客户端")
    print("=" * 60)
    
    client = get_mcp_client()
    
    # 测试用例 1: 兼容的组合
    print("\n测试用例 1: 九号 E100 + Lingbo-72182 (应该兼容)")
    print("-" * 60)
    result1 = client.query_controller_compatibility(
        vehicle_model="九号 E100",
        controller_model="Lingbo-72182",
        controller_brand="Lingbo"
    )
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    
    # 测试用例 2: 不兼容的组合
    print("\n测试用例 2: 九号 E100 + Lingbo-72180 (应该不兼容)")
    print("-" * 60)
    result2 = client.query_controller_compatibility(
        vehicle_model="九号 E100",
        controller_model="Lingbo-72180",
        controller_brand="Lingbo"
    )
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    
    # 测试用例 3: 未知的组合
    print("\n测试用例 3: 未知车型 + 未知控制器 (应该返回未知)")
    print("-" * 60)
    result3 = client.query_controller_compatibility(
        vehicle_model="未知车型",
        controller_model="未知控制器",
        controller_brand="未知品牌"
    )
    print(json.dumps(result3, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ MCP 客户端测试完成")
    print("=" * 60)


def test_execute_mcp_tool():
    """测试 _execute_mcp_tool 方法"""
    print("\n" + "=" * 60)
    print("测试 _execute_mcp_tool 方法")
    print("=" * 60)

    # 直接测试 MCP 工具调用逻辑，不涉及完整的 Agent
    client = get_mcp_client()

    # 模拟步骤配置
    step_config = {
        "id": "step_2_match",
        "mcp_tool": {
            "name": "query_controller_compatibility"
        }
    }

    # 模拟状态
    state = {
        "customer_info": {
            "vehicle_model": "九号 E100",
            "controller_model": "Lingbo-72182",
            "controller_brand": "Lingbo"
        }
    }

    print("\n步骤配置:")
    print(json.dumps(step_config, ensure_ascii=False, indent=2))

    print("\n状态:")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    # 模拟 _execute_mcp_tool 的逻辑
    print("\n执行 MCP 工具调用...")
    tool_config = step_config.get("mcp_tool", {})
    tool_name = tool_config.get("name")

    if tool_name == "query_controller_compatibility":
        customer_info = state.get("customer_info", {})
        vehicle_model = customer_info.get("vehicle_model")
        controller_model = customer_info.get("controller_model")
        controller_brand = customer_info.get("controller_brand")

        result = client.query_controller_compatibility(
            vehicle_model=vehicle_model,
            controller_model=controller_model,
            controller_brand=controller_brand
        )

        tool_result = {
            "success": True,
            "error": None,
            "data": result
        }
    else:
        tool_result = {
            "success": False,
            "error": f"未知的工具: {tool_name}",
            "data": None
        }

    print("\n工具调用结果:")
    print(json.dumps(tool_result, ensure_ascii=False, indent=2))

    # 模拟生成响应消息和流程控制
    print("\n生成响应消息和流程控制...")
    if tool_result["success"]:
        data = tool_result["data"]
        if data.get("compatible") is True:
            # 兼容，自动进入下一步
            response_msg = f"正在为您核对控制器与车型的匹配性，请稍候...\n\n✅ 核对结果：{data.get('reason', '兼容')}\n\n请拍一张转接线插头的照片，我要确认：1.是否插紧 2.防呆口方向 3.霍尔线序。"
            next_action = "自动进入 step_3_wiring（检查转接线）"
        elif data.get("compatible") is False:
            # 不兼容，流程结束
            response_msg = f"经核对，您手里的控制器版本与车型暂不匹配（批次差异）。辛苦您寄回，我们为您更换适配版本。"
            if data.get("alternative"):
                response_msg += f"\n\n💡 推荐使用：{data['alternative']}"
            next_action = "流程结束（不兼容）"
        else:
            # 未知，等待用户确认
            response_msg = f"正在为您核对控制器与车型的匹配性，请稍候...\n\n⚠️ {data.get('reason', '无法确定兼容性')}\n\n请确认是否继续排查？"
            next_action = "等待用户确认"

        print(f"\n响应消息:\n{response_msg}")
        print(f"\n下一步动作: {next_action}")
    else:
        print(f"\n⚠️ 工具调用失败: {tool_result['error']}")

    print("\n" + "=" * 60)
    print("✅ _execute_mcp_tool 方法测试完成")
    print("=" * 60)


def test_auto_flow_continuation():
    """测试自动流程继续功能"""
    print("\n" + "=" * 60)
    print("测试自动流程继续功能")
    print("=" * 60)

    print("\n场景：控制器兼容，应该自动进入下一步（检查转接线）")
    print("-" * 60)

    # 模拟 YAML 配置
    steps = [
        {
            "id": "step_1_voltage",
            "prompt": "请确认全车电压是多少。"
        },
        {
            "id": "step_2_match",
            "prompt": "正在为您核对控制器与车型的匹配性，请稍候...",
            "mcp_tool": {"name": "query_controller_compatibility"},
            "on_success": {"next": "step_3_wiring"}
        },
        {
            "id": "step_3_wiring",
            "prompt": "请拍一张转接线插头的照片，我要确认：1.是否插紧 2.防呆口方向 3.霍尔线序。"
        }
    ]

    # 模拟当前状态：用户刚回答完 step_1（电压）
    current_step_idx = 0
    next_step_idx = 1  # 准备进入 step_2_match

    print(f"\n当前步骤: {current_step_idx} ({steps[current_step_idx]['id']})")
    print(f"下一步骤: {next_step_idx} ({steps[next_step_idx]['id']})")

    # 模拟 MCP 工具调用结果（兼容）
    tool_result = {
        "success": True,
        "data": {
            "compatible": True,
            "reason": "该控制器型号与车型完全匹配"
        }
    }

    print(f"\nMCP 工具调用结果: compatible = {tool_result['data']['compatible']}")

    # 模拟自动流程继续逻辑
    next_step = steps[next_step_idx]
    on_success = next_step.get("on_success", {})
    next_next_step_id = on_success.get("next")

    # 查找下一步的索引
    next_next_step_idx = next_step_idx + 1
    if next_next_step_id:
        for idx, s in enumerate(steps):
            if s.get("id") == next_next_step_id:
                next_next_step_idx = idx
                break

    next_next_step = steps[next_next_step_idx]

    # 生成响应消息
    response_msg = f"{next_step['prompt']}\n\n✅ 核对结果：{tool_result['data']['reason']}\n\n{next_next_step['prompt']}"

    print(f"\n自动进入步骤: {next_next_step_idx} ({next_next_step['id']})")
    print(f"\n完整响应消息:\n{response_msg}")

    print("\n" + "=" * 60)
    print("✅ 自动流程继续功能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 测试 MCP 客户端
    test_mcp_client()

    # 测试 _execute_mcp_tool 方法
    test_execute_mcp_tool()

    # 测试自动流程继续功能
    test_auto_flow_continuation()

