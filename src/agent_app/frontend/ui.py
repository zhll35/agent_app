import streamlit as st
import requests
import uuid
import json

# 后端 API 地址
API_URL = "http://localhost:8000/chat"

# 页面配置
try:
    st.set_page_config(
        page_title="电动车售后智能客服",
        page_icon="🔧",
        layout="wide"
    )
except Exception as e:
    # 如果页面配置已经设置过，会抛出异常，这是正常的
    pass

# --- 1. Session State 初始化 ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！我是普小售后智能助手。请问有什么可以帮您？"}
    ]

# --- 2. 侧边栏：模拟车辆信息 (Mock DB) ---
# 在真实场景中，这些信息通常来自 CRM 数据库。
# 在这里，我们允许手动输入以测试 Agent 的“信息采集”和“木桶原理计算”逻辑。
with st.sidebar:
    st.header("🛠️ 模拟车辆档案 (Mock DB)")
    st.caption("修改此处参数模拟数据库中的客户车辆信息")
    
    with st.expander("基础信息", expanded=True):
        order_id = st.text_input("订单号", value="ORDER-2024001")
        vehicle_model = st.selectbox("车型", ["", "九号 E100", "小牛 NQI", "其它"], index=1)
        controller_model = st.text_input("控制器型号", value="Lingbo-72182")
    
    with st.expander("电池系统 (决定木桶短板)", expanded=True):
        battery_type = st.selectbox("电池类型", ["lead_acid", "lithium"], index=1, format_func=lambda x: "锂电池" if x == "lithium" else "铅酸电池")
        voltage = st.number_input("电压 (V)", value=72.0, step=12.0)
        # 根据电池类型动态显示输入框
        capacity_ah = None
        bms_current = None
        if battery_type == "lead_acid":
            capacity_ah = st.number_input("容量 (Ah)", value=20.0)
        else:
            bms_current = st.number_input("保护板持续电流 (A)", value=50.0, help="非常重要的安全参数")

    with st.expander("电机与线路", expanded=False):
        motor_power = st.number_input("电机额定功率 (W)", value=1200.0)
        motor_type = st.selectbox("电机类型", ["standard", "performance"], index=0)
        wire_gauge = st.number_input("主线线径 (mm²)", value=6.0)
        breaker_rating = st.number_input("空开规格 (A)", value=80.0)
        controller_max = st.number_input("控标称电流 (A)", value=150.0)

    if st.button("重置对话", type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [{"role": "assistant", "content": "会话已重置。请问有什么可以帮您？"}]
        st.rerun()

# --- 3. 构造请求 Payload ---
def get_mock_info():
    """将侧边栏数据打包为字典"""
    info = {
        "order_id": order_id,
        "vehicle_model": vehicle_model,
        "controller_model": controller_model,
        "battery_type": battery_type,
        "voltage": voltage,
        "motor_power": motor_power,
        "wire_gauge": wire_gauge,
        "breaker_rating": breaker_rating,
        "controller_max_current": controller_max
    }
    if battery_type == "lead_acid":
        info["capacity_ah"] = capacity_ah
    else:
        info["bms_current"] = bms_current
    
    # 过滤空值，模拟真实数据缺失的情况
    return {k: v for k, v in info.items() if v}

# --- 4. 聊天界面渲染 ---
st.title("🔧 普小售后智能诊断系统")

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. 处理用户输入与后端交互 ---
if prompt := st.chat_input("描述您的问题，例如：我想调大电流..."):
    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用后端 API
    try:
        payload = {
            "message": prompt,
            "thread_id": st.session_state.session_id,
            "mock_info": get_mock_info()  # 实时传入侧边栏数据
        }
        
        with st.spinner("AI 正在诊断中..."):
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            ai_reply = data["response"]
            
            # 可视化调试信息（可选）
            if not data.get("is_info_complete"):
                with st.expander("🔍 系统提示：信息不全", expanded=False):
                    st.warning("Agent 正在尝试收集更多信息，请配合回答。")

    except Exception as e:
        ai_reply = f"❌ 连接服务器失败: {str(e)}\n请确保后端服务 (`server.py`) 已在端口 8000 启动。"

    # 3. 显示 AI 回复
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)