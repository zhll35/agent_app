from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_app.graph.build import build_graph
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="电动售后智能客服", version="0.1.0")

# 初始化图实例
logger.info("正在初始化 Agent Graph...")
agent_graph = build_graph()
logger.info("Agent Graph 初始化完成")

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    # 模拟前端传入的用户信息（实际场景可能从数据库取）
    mock_info: dict = {}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    logger.info(f"收到聊天请求 - Thread ID: {req.thread_id}")
    logger.debug(f"用户消息: {req.message}")
    logger.debug(f"客户信息: {json.dumps(req.mock_info, ensure_ascii=False, indent=2)}")

    try:
        config = {"configurable": {"thread_id": req.thread_id}}

        # 构造初始状态
        # 注意：langgraph 会自动合并新消息
        input_state = {
            "messages": [("user", req.message)],
            "customer_info": req.mock_info
        }

        logger.info("开始执行 Agent Graph...")
        logger.debug(f"输入状态: {json.dumps(input_state, ensure_ascii=False, default=str)}")

        # 执行图
        result = agent_graph.invoke(input_state, config=config)

        logger.info("Agent Graph 执行完成")
        logger.debug(f"执行结果状态:")
        logger.debug(f"  - is_info_complete: {result.get('is_info_complete')}")
        logger.debug(f"  - current_step: {result.get('current_step')}")
        logger.debug(f"  - diagnostic_result: {result.get('diagnostic_result')}")
        logger.debug(f"  - 消息数量: {len(result.get('messages', []))}")

        # 获取最新的 AI 回复
        last_msg = result["messages"][-1]
        logger.debug(f"最后一条消息类型: {type(last_msg)}")
        logger.debug(f"最后一条消息内容: {last_msg.content if hasattr(last_msg, 'content') else last_msg}")

        response_data = {
            "response": last_msg.content,
            "current_step": result.get("current_step"),
            "is_info_complete": result.get("is_info_complete")
        }

        logger.info(f"返回响应: {response_data['response'][:100]}...")
        return response_data

    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)