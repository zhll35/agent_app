import yaml
from pathlib import Path
from typing import Dict, Any
import logging
import json
from langchain_core.prompts import ChatPromptTemplate
from agent_app.agents.base import BaseAgent
from agent_app.graph.state import AgentState
from agent_app.tools import get_mcp_client

logger = logging.getLogger(__name__)

class DiagnosticAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.sop_config = self._load_sop_config()
        self.mcp_client = get_mcp_client()

    def _load_sop_config(self):
        """加载 YAML 配置"""
        # __file__ 是 .../src/agent_app/agents/executor.py
        # parent 是 .../src/agent_app/agents
        # parent.parent 是 .../src/agent_app
        path = Path(__file__).parent.parent / "knowledge/templates/sop_diagnostic.yaml"
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _execute_mcp_tool(self, step: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        执行 MCP 工具调用

        Args:
            step: 当前步骤配置
            state: 当前状态

        Returns:
            工具调用结果
        """
        tool_config = step.get("mcp_tool", {})
        tool_name = tool_config.get("name")

        logger.info(f"执行 MCP 工具: {tool_name}")

        if tool_name == "query_controller_compatibility":
            # 从状态中获取参数
            customer_info = state.get("customer_info", {})
            vehicle_model = customer_info.get("vehicle_model")
            controller_model = customer_info.get("controller_model")
            controller_brand = customer_info.get("controller_brand")

            if not vehicle_model or not controller_model:
                logger.warning("缺少必要参数：vehicle_model 或 controller_model")
                return {
                    "success": False,
                    "error": "缺少车型或控制器型号信息",
                    "data": None
                }

            # 调用 MCP 工具
            try:
                result = self.mcp_client.query_controller_compatibility(
                    vehicle_model=vehicle_model,
                    controller_model=controller_model,
                    controller_brand=controller_brand
                )

                logger.info(f"MCP 工具调用成功: {json.dumps(result, ensure_ascii=False)}")

                return {
                    "success": True,
                    "error": None,
                    "data": result
                }
            except Exception as e:
                logger.error(f"MCP 工具调用失败: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "data": None
                }
        else:
            logger.error(f"未知的 MCP 工具: {tool_name}")
            return {
                "success": False,
                "error": f"未知的工具: {tool_name}",
                "data": None
            }

    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """执行诊断逻辑"""
        current_step_idx = state.get("current_step", 0)
        steps = self.sop_config["steps"]

        logger.info(f"DiagnosticAgent 执行 - 当前步骤: {current_step_idx}/{len(steps)}")

        # 1. 检查流程是否结束
        if current_step_idx >= len(steps):
            logger.info("诊断流程已完成")
            return {
                "messages": [("assistant", "标准诊断流程已结束。")],
                "diagnostic_result": "completed"
            }

        step = steps[current_step_idx]
        logger.debug(f"当前步骤配置: {step}")

        # 检查 prompt 字段是否存在
        if "prompt" not in step:
            logger.error(f"步骤 {current_step_idx} 缺少 'prompt' 字段: {step}")
            return {
                "messages": [("assistant", f"配置错误：步骤 {step.get('id', current_step_idx)} 缺少提示信息")],
                "diagnostic_result": "error"
            }

        # 2. 生成 LLM 的执行 Prompt
        # 这里我们利用 LLM 来判断用户的上一条回复是否满足了当前步骤的要求
        # 如果是刚进入该步骤，则直接输出 Prompt

        last_message = state["messages"][-1]
        logger.debug(f"最后一条消息类型: {last_message.type}")

        if last_message.type == "human":
            # 用户回复了，需要校验逻辑
            logger.info(f"用户已回复，准备进入下一步")

            # TODO: 这里应该调用 LLM 进行校验
            # validation_prompt = ChatPromptTemplate.from_template(...)
            # result = self.llm.invoke(...)

            # 简化逻辑：假设通过，进入下一步
            next_step_idx = current_step_idx + 1
            logger.info(f"进入下一步: {next_step_idx}")

            if next_step_idx >= len(steps):
                # 已经是最后一步，返回完成消息
                logger.info("已到达最后一步，诊断完成")
                return {
                    "messages": [("assistant", "诊断步骤已全部完成，感谢您的配合！")],
                    "current_step": next_step_idx,
                    "diagnostic_result": "completed"
                }
            else:
                # 输出下一步的问题
                next_step = steps[next_step_idx]

                # 检查下一步是否有 prompt
                if "prompt" not in next_step:
                    logger.error(f"下一步骤 {next_step_idx} 缺少 'prompt' 字段: {next_step}")
                    return {
                        "messages": [("assistant", f"配置错误：步骤 {next_step.get('id', next_step_idx)} 缺少提示信息")],
                        "current_step": next_step_idx,
                        "diagnostic_result": "error"
                    }

                # 检查下一步是否需要调用 MCP 工具
                if "mcp_tool" in next_step:
                    logger.info(f"下一步需要调用 MCP 工具: {next_step.get('mcp_tool', {}).get('name')}")

                    # 执行 MCP 工具调用
                    tool_result = self._execute_mcp_tool(next_step, state)

                    if tool_result["success"]:
                        # 工具调用成功，根据结果决定下一步
                        data = tool_result["data"]

                        # 检查兼容性结果
                        if data.get("compatible") is True:
                            # 兼容，自动继续到下一步
                            logger.info(f"控制器兼容，自动进入下一步")

                            # 获取 on_success 配置
                            on_success = next_step.get("on_success", {})
                            next_next_step_id = on_success.get("next")

                            # 查找下一步的索引
                            next_next_step_idx = next_step_idx + 1
                            if next_next_step_id:
                                # 如果配置了 next，查找对应的步骤
                                for idx, s in enumerate(steps):
                                    if s.get("id") == next_next_step_id:
                                        next_next_step_idx = idx
                                        break

                            # 检查是否超出范围
                            if next_next_step_idx >= len(steps):
                                logger.info("已到达最后一步")
                                response_msg = f"{next_step['prompt']}\n\n✅ 核对结果：{data.get('reason', '兼容')}\n\n诊断步骤已全部完成，感谢您的配合！"
                                return {
                                    "messages": [("assistant", response_msg)],
                                    "current_step": next_next_step_idx,
                                    "diagnostic_result": "completed",
                                    "tool_result": tool_result
                                }

                            # 获取下一步配置
                            next_next_step = steps[next_next_step_idx]

                            # 生成包含兼容性结果和下一步问题的消息
                            response_msg = f"{next_step['prompt']}\n\n✅ 核对结果：{data.get('reason', '兼容')}\n\n{next_next_step['prompt']}"

                            logger.info(f"自动进入步骤 {next_next_step_idx}: {next_next_step.get('id')}")
                            return {
                                "messages": [("assistant", response_msg)],
                                "current_step": next_next_step_idx,
                                "tool_result": tool_result
                            }
                        elif data.get("compatible") is False:
                            # 不兼容，返回失败消息，流程结束
                            on_fail = next_step.get("on_fail", {})
                            fail_msg = on_fail.get("message", "控制器与车型不匹配")

                            # 如果有推荐的替代型号，添加到消息中
                            if data.get("alternative"):
                                fail_msg += f"\n\n💡 推荐使用：{data['alternative']}"

                            response_msg = fail_msg

                            logger.info(f"控制器不兼容，流程结束")
                            return {
                                "messages": [("assistant", response_msg)],
                                "current_step": next_step_idx,
                                "diagnostic_result": "failed",
                                "tool_result": tool_result
                            }
                        else:
                            # 未知，返回提示，等待用户确认
                            response_msg = f"{next_step['prompt']}\n\n⚠️ {data.get('reason', '无法确定兼容性')}\n\n请确认是否继续排查？"

                            logger.info(f"兼容性未知，等待用户确认")
                            return {
                                "messages": [("assistant", response_msg)],
                                "current_step": next_step_idx,
                                "tool_result": tool_result
                            }
                    else:
                        # 工具调用失败，降级处理
                        logger.warning(f"MCP 工具调用失败: {tool_result['error']}")
                        response_msg = f"{next_step['prompt']}\n\n⚠️ 自动核对失败，将为您人工核对"
                        return {
                            "messages": [("assistant", response_msg)],
                            "current_step": next_step_idx
                        }
                else:
                    # 不需要调用工具，直接输出问题
                    logger.info(f"输出下一步问题: {next_step['prompt'][:50]}...")
                    return {
                        "messages": [("assistant", next_step["prompt"])],
                        "current_step": next_step_idx
                    }
        else:
            # 刚进入步骤，输出问题
            logger.info(f"首次进入步骤 {current_step_idx}，输出问题")
            return {
                "messages": [("assistant", step["prompt"])],
                "current_step": current_step_idx
            }

diagnostic_agent = DiagnosticAgent()