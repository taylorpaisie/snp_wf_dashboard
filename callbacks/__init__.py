from .tree_callbacks import register_tree_callbacks
from .snp_callbacks import register_snp_callbacks
from .alignment_callbacks import register_alignment_callbacks

def register_callbacks(app):
    """Register all callback functions."""
    register_tree_callbacks(app)
    register_snp_callbacks(app)
    register_alignment_callbacks(app)
