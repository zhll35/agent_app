#!/usr/bin/env python3
"""
测试诊断流程的完整交互
验证 Checkpoint 和多步骤流程是否正常工作
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
THREAD_ID = f"test-{int(time.time())}"

def send_message(message: str, mock_info: dict = None):
    """发送消息到服务器"""
    if mock_info is None:
        mock_info = {}
    
    payload = {
        "message": message,
        "thread_id": THREAD_ID,
        "mock_info": mock_info
    }
    
    print(f"\n{'='*60}")
    print(f"📤 发送消息: {message}")
    print(f"🆔 Thread ID: {THREAD_ID}")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"📥 服务器响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None

def main():
    print("🚀 开始测试诊断流程")
    print(f"🆔 使用 Thread ID: {THREAD_ID}")
    
    # 步骤 1: 首次请求 - 触发信息收集
    print("\n" + "="*60)
    print("步骤 1: 首次请求 - 应该触发信息收集")
    print("="*60)
    result1 = send_message("我想调大电流")
    
    if not result1:
        print("❌ 测试失败：无法连接到服务器")
        print("💡 请确保服务器正在运行: ./start_debug.sh")
        return
    
    time.sleep(1)
    
    # 步骤 2: 补充信息 - 应该进入诊断流程
    print("\n" + "="*60)
    print("步骤 2: 补充信息 - 应该进入诊断流程第一步")
    print("="*60)
    result2 = send_message(
        "九号 E100, Lingbo-72182",
        mock_info={
            "vehicle_model": "九号 E100",
            "controller_model": "Lingbo-72182",
            "controller_brand": "Lingbo",
            "battery_voltage": 72
        }
    )
    
    time.sleep(1)
    
    # 步骤 3: 回答第一步（电压）- 应该进入第二步
    print("\n" + "="*60)
    print("步骤 3: 回答电压 - 应该进入第二步（核对匹配性）")
    print("="*60)
    result3 = send_message("72V")
    
    time.sleep(1)
    
    # 步骤 4: 继续下一步 - 应该进入第三步
    print("\n" + "="*60)
    print("步骤 4: 继续 - 应该进入第三步（检查转接线）")
    print("="*60)
    result4 = send_message("好的")
    
    time.sleep(1)
    
    # 步骤 5: 上传图片（模拟）- 应该进入第四步
    print("\n" + "="*60)
    print("步骤 5: 上传图片 - 应该进入第四步（电机自学习）")
    print("="*60)
    result5 = send_message("已上传图片")
    
    time.sleep(1)
    
    # 步骤 6: 确认自学习 - 应该进入第五步
    print("\n" + "="*60)
    print("步骤 6: 确认自学习 - 应该进入第五步（协议检查）")
    print("="*60)
    result6 = send_message("是的，已经做过自学习")
    
    time.sleep(1)
    
    # 步骤 7: 最后一步 - 应该完成诊断
    print("\n" + "="*60)
    print("步骤 7: 最后一步 - 应该完成诊断")
    print("="*60)
    result7 = send_message("协议设置正确")
    
    # 总结
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print("\n📊 测试总结:")
    print(f"  - Thread ID: {THREAD_ID}")
    print(f"  - 总共发送: 7 条消息")
    print(f"  - 预期流程: 信息收集 → 步骤1 → 步骤2 → 步骤3 → 步骤4 → 步骤5 → 完成")
    print("\n💡 检查要点:")
    print("  1. 每次请求都应该返回不同的响应（不是重复要求输入电压）")
    print("  2. current_step 应该逐步递增")
    print("  3. 最后应该显示诊断完成")
    print("\n📝 查看详细日志:")
    print("  - 服务器终端应该显示详细的执行日志")
    print("  - 包括: 当前步骤、路由决策、状态更新等")

if __name__ == "__main__":
    main()

