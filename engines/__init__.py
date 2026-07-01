"""AuditScope 计算引擎(纯函数,可单测,不依赖 UI / DB)。"""
from .materiality import compute_materiality
from .component_scoping import score_components
from .account_scoping import score_accounts

__all__ = ["compute_materiality", "score_components", "score_accounts"]
