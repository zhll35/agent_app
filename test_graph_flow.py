"""测试图流程是否正常"""
from agent_app.graph.build import build_graph

# 构建图
graph = build_graph()

# 测试场景：信息完整的情况
test_state = {
    "messages": [("user", "我想调大电流")],
    "customer_info": {
        "order_id": "ORDER-2024001",
        "vehicle_model": "九号 E100",
        "controller_model": "Lingbo-72182",
        "battery_type": "lithium",
        "voltage": 72.0,
        "bms_current": 50.0,
        "motor_power": 1200.0,
        "wire_gauge": 6.0,
        "breaker_rating": 80.0,
        "controller_max_current": 150.0
    }
}

config = {"configurable": {"thread_id": "test-123"}}

print("=" * 60)
print("测试：信息完整的情况")
print("=" * 60)

result = graph.invoke(test_state, config=config)

print("\n最终状态：")
print(f"is_info_complete: {result.get('is_info_complete')}")
print(f"current_step: {result.get('current_step')}")
print(f"diagnostic_result: {result.get('diagnostic_result')}")
print(f"\n消息历史 ({len(result['messages'])} 条):")
for i, msg in enumerate(result["messages"]):
    role = msg.type if hasattr(msg, 'type') else 'unknown'
    content = msg.content if hasattr(msg, 'content') else str(msg)
    print(f"  [{i+1}] {role}: {content[:100]}...")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

