"""
模板加载器 - 电动车售后诊断模板管理

注意：此模块当前未在主工作流中使用。
电动车售后诊断直接在 DiagnosticAgent 中加载 sop_diagnostic.yaml。
此文件保留用于未来可能的多模板管理需求。
"""
import yaml
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent / "templates"

class TemplateLoader:
    """YAML 模板加载器（预留）"""

    @staticmethod
    def load_template(template_name: str) -> Dict[str, Any]:
        """
        加载诊断模板

        Args:
            template_name: 模板名称，例如 "sop_diagnostic"

        Returns:
            模板内容字典
        """
        file_path = BASE_DIR / f"{template_name}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Template not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)