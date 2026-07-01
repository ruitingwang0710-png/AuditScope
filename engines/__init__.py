"""AuditScope calculation engines (pure functions, unit-testable, no UI/DB deps)."""
from .materiality import compute_materiality
from .component_scoping import score_components
from .account_scoping import score_accounts
from .hashing import generate_transaction_hash, add_hashes, duplicate_hash_groups
from .sampling import select_samples

__all__ = [
    "compute_materiality", "score_components", "score_accounts",
    "generate_transaction_hash", "add_hashes", "duplicate_hash_groups",
    "select_samples",
]
