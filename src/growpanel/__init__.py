"""GrowPanel Python SDK — subscription analytics REST API client.

Usage:
    from growpanel import GrowPanel

    gp = GrowPanel(api_key="gp_...")
    summary = gp.reports.summary()
    print(summary.mrr_current)
"""

from .client import GrowPanel
from .errors import GrowPanelError

__all__ = ["GrowPanel", "GrowPanelError"]
__version__ = "0.1.0"
