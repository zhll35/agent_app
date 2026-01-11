from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class CustomerInfo(TypedDict):
    order_id: Optional[str]
    vehicle_model: Optional[str]
    controller_model: Optional[str]
    controller_brand: Optional[str] # Lingbo, Leiting, etc.
    battery_type: Optional[str]     # lead_acid, lithium
    battery_voltage: Optional[float]
    bms_current: Optional[float]    # 锂电保护板电流
    motor_power: Optional[float]
    wire_gauge: Optional[float]     # 主线平方数
    breaker_rating: Optional[float] # 空开安数

class AgentState(TypedDict):
    # 消息历史，自动追加
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 业务状态上下文
    customer_info: CustomerInfo
    is_info_complete: bool
    current_step: int             # SOP 当前步骤索引
    diagnostic_result: Optional[str]