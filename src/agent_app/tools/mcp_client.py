"""
MCP (Model Context Protocol) 工具客户端
用于调用外部 MCP 服务查询控制器配件信息
"""

import logging
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP 工具客户端"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 MCP 客户端
        
        Args:
            base_url: MCP 服务的基础 URL，如果为 None 则使用模拟数据
        """
        self.base_url = base_url
        self.use_mock = base_url is None
        
        if self.use_mock:
            logger.info("MCP 客户端使用模拟数据模式")
        else:
            logger.info(f"MCP 客户端连接到: {base_url}")
    
    def query_controller_compatibility(
        self, 
        vehicle_model: str, 
        controller_model: str,
        controller_brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询控制器与车型的兼容性
        
        Args:
            vehicle_model: 车型，例如 "九号 E100"
            controller_model: 控制器型号，例如 "Lingbo-72182"
            controller_brand: 控制器品牌，例如 "Lingbo"
        
        Returns:
            包含兼容性信息的字典：
            {
                "compatible": bool,  # 是否兼容
                "confidence": float,  # 置信度 0-1
                "reason": str,  # 原因说明
                "alternative": str | None,  # 推荐的替代型号
                "details": dict  # 详细信息
            }
        """
        logger.info(f"查询控制器兼容性: 车型={vehicle_model}, 控制器={controller_model}")
        
        if self.use_mock:
            return self._mock_query_compatibility(vehicle_model, controller_model, controller_brand)
        else:
            return self._real_query_compatibility(vehicle_model, controller_model, controller_brand)
    
    def _mock_query_compatibility(
        self, 
        vehicle_model: str, 
        controller_model: str,
        controller_brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """模拟查询（用于开发和测试）"""
        
        # 模拟数据库
        compatibility_db = {
            ("九号 E100", "Lingbo-72182"): {
                "compatible": True,
                "confidence": 0.95,
                "reason": "该控制器型号与车型完全匹配，已在多个批次中验证",
                "alternative": None,
                "details": {
                    "voltage_match": True,
                    "power_match": True,
                    "protocol_match": True,
                    "tested_batches": ["2023-Q1", "2023-Q2", "2023-Q3"],
                    "success_rate": 0.98
                }
            },
            ("九号 E100", "Lingbo-72180"): {
                "compatible": False,
                "confidence": 0.90,
                "reason": "该控制器型号与车型不匹配，电压规格不符",
                "alternative": "Lingbo-72182",
                "details": {
                    "voltage_match": False,
                    "power_match": True,
                    "protocol_match": True,
                    "issue": "电压规格：控制器60V，车型需要72V"
                }
            },
            ("小牛 N1S", "Leiting-60150"): {
                "compatible": True,
                "confidence": 0.92,
                "reason": "该控制器型号与车型兼容，需要注意协议设置",
                "alternative": None,
                "details": {
                    "voltage_match": True,
                    "power_match": True,
                    "protocol_match": True,
                    "note": "需要设置为 CAN 协议"
                }
            }
        }
        
        # 查找匹配
        key = (vehicle_model, controller_model)
        if key in compatibility_db:
            result = compatibility_db[key]
        else:
            # 默认返回未知
            result = {
                "compatible": None,  # 未知
                "confidence": 0.5,
                "reason": f"未找到 {vehicle_model} 与 {controller_model} 的兼容性记录，建议人工核对",
                "alternative": None,
                "details": {
                    "status": "unknown",
                    "suggestion": "请联系技术支持确认兼容性"
                }
            }
        
        logger.debug(f"模拟查询结果: {json.dumps(result, ensure_ascii=False)}")
        return result
    
    def _real_query_compatibility(
        self, 
        vehicle_model: str, 
        controller_model: str,
        controller_brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """真实的 MCP 服务查询"""
        # TODO: 实现真实的 MCP 服务调用
        # 这里应该调用实际的 MCP 服务 API
        
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/query/controller_compatibility",
                json={
                    "vehicle_model": vehicle_model,
                    "controller_model": controller_model,
                    "controller_brand": controller_brand
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP 服务调用失败: {e}")
            # 降级到模拟数据
            logger.warning("降级到模拟数据模式")
            return self._mock_query_compatibility(vehicle_model, controller_model, controller_brand)


# 全局单例
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """获取 MCP 客户端单例"""
    global _mcp_client
    if _mcp_client is None:
        # TODO: 从配置中读取 MCP 服务 URL
        # from agent_app.settings import settings
        # _mcp_client = MCPClient(base_url=settings.MCP_BASE_URL)
        
        # 目前使用模拟模式
        _mcp_client = MCPClient(base_url=None)
    return _mcp_client

