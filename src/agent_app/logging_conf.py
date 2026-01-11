from __future__ import annotations

import logging
from .settings import get_settings

def configure_logging() -> None:
    s = get_settings()
    logging.basicConfig(
        level=getattr(logging, s.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
