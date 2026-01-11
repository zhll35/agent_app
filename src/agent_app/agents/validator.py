from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
import math

# 常量定义 [cite: 105, 106, 113, 114]
MOTOR_COEFF_STANDARD = 3.5  # 直片电机/普通瓦片
MOTOR_COEFF_PERFORMANCE = 6.0  # WP/高性能瓦片
WIRE_CURRENT_PER_SQMM = 12.0  # 每平方毫米线径承载电流
SAFE_TEMP_MOTOR = 100.0       # 电机安全温度
SAFE_TEMP_CONTROLLER = 90.0   # 控制器安全温度

class VehicleSpecs(BaseModel):
    """车辆参数输入模型"""
    
    # 电池参数 [cite: 24, 25, 26]
    battery_type: Literal["lead_acid", "lithium"] = Field(..., description="电池类型：铅酸或锂电")
    voltage: float = Field(..., description="电池电压(V)", examples=[48, 60, 72])
    capacity_ah: Optional[float] = Field(None, description="电池容量(Ah)，铅酸必填")
    bms_current: Optional[float] = Field(None, description="保护板持续电流(A)，锂电必填")

    # 电机参数 [cite: 19, 105]
    motor_power_rated: float = Field(..., description="电机额定功率(W)")
    motor_type: Literal["standard", "performance"] = Field(
        "standard", 
        description="电机类型：standard(直片/普通瓦片), performance(WP/高性能)"
    )

    # 线路与硬件 [cite: 29, 106, 107, 108]
    wire_gauge: float = Field(..., description="主线线径(平方毫米)")
    breaker_rating: float = Field(..., description="空开额定电流(A)")
    controller_max_current: float = Field(..., description="控制器标称最大电流(A)")

    @model_validator(mode='after')
    def check_battery_fields(self):
        """校验电池类型对应的必填项"""
        if self.battery_type == 'lead_acid' and not self.capacity_ah:
            raise ValueError("铅酸电池必须提供容量(Ah)")
        if self.battery_type == 'lithium' and not self.bms_current:
            raise ValueError("锂电池必须提供保护板持续电流(A) [cite: 26]")
        return self

class SafetyCalculator:
    """木桶原理计算器 [cite: 103-111]"""

    @staticmethod
    def calculate_max_bus_current(specs: VehicleSpecs) -> Dict[str, Any]:
        limits = {}

        # 1. 电池短板计算 [cite: 104]
        if specs.battery_type == "lead_acid":
            # 铅酸电池容量 * 2.5
            limits["battery"] = specs.capacity_ah * 2.5 
        else:
            # 锂电池直接取保护板电流
            limits["battery"] = specs.bms_current

        # 2. 电机短板计算 [cite: 105]
        # 公式：额定功率 * 系数 / 电压
        coeff = MOTOR_COEFF_PERFORMANCE if specs.motor_type == "performance" else MOTOR_COEFF_STANDARD
        limits["motor"] = (specs.motor_power_rated * coeff) / specs.voltage

        # 3. 主线短板计算 [cite: 106]
        # 线径 * 12A
        limits["wire"] = specs.wire_gauge * WIRE_CURRENT_PER_SQMM

        # 4. 空开短板计算 [cite: 107]
        # 额定值 * 80%
        limits["breaker"] = specs.breaker_rating * 0.8

        # 5. 控制器短板计算 [cite: 108]
        # 标称值 * 80%
        limits["controller"] = specs.controller_max_current * 0.8

        # 取最小值 (木桶原理) [cite: 103]
        safe_current = min(limits.values())
        bottleneck = min(limits, key=limits.get)

        return {
            "safe_bus_current": round(safe_current, 1),
            "bottleneck_component": bottleneck,  # 系统的短板组件
            "details": limits,
            "warning": SafetyCalculator._generate_warning(bottleneck, safe_current)
        }

    @staticmethod
    def _generate_warning(bottleneck: str, value: float) -> str:
        """生成风险提示话术 [cite: 79]"""
        msgs = {
            "battery": f"系统短板在电池。建议母线电流不超过 {value}A，否则可能导致电池过热或保护板断电。",
            "wire": f"系统短板在主线。建议母线电流不超过 {value}A，否则可能导致线路发热熔断。",
            "motor": f"系统短板在电机。建议母线电流不超过 {value}A，强行加大电流可能导致电机退磁。",
        }
        return msgs.get(bottleneck, f"建议最大母线电流设定为 {value}A。")

# 使用示例
if __name__ == "__main__":
    # 模拟 [cite: 109-111] 的案例
    test_data = VehicleSpecs(
        battery_type="lead_acid",
        voltage=72,
        capacity_ah=30,
        motor_power_rated=1000,
        motor_type="standard",
        wire_gauge=6,
        breaker_rating=80,
        controller_max_current=150
    )
    result = SafetyCalculator.calculate_max_bus_current(test_data)
    print(result) 
    # 预期输出: safe_bus_current: 48.6, bottleneck: motor