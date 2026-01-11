"""
模板注册中心 - 电动车售后诊断模板选择

注意：此模块当前未在主工作流中使用。
电动车售后诊断直接在 DiagnosticAgent 中加载 sop_diagnostic.yaml。
此文件保留用于未来可能的多模板管理需求。
"""
from __future__ import annotations
from typing import Dict, Any
from .loader import TemplateLoader

def select_template(template_name: str = "sop_diagnostic") -> Dict[str, Any]:
    """
    选择并加载诊断模板（预留）

    Args:
        template_name: 模板名称，默认为 "sop_diagnostic"

    Returns:
        模板内容字典
    """
    return TemplateLoader.load_template(template_name)
