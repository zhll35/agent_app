from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agent_app.settings import settings

@dataclass
class AgentResult:
    ok: bool
    data: Dict[str, Any]
    error: str | None = None

class BaseAgent:
    """所有 Agent 的基类，提供 LLM 访问"""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0
        )
