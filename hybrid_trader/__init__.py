"""
Hybrid Trader: Unified Python Library for Korean Stock & Crypto Automated Trading

Seamlessly integrate Korea Investment & Securities API (KIS) with Upbit API
to build sophisticated hybrid trading systems with just a few lines of code.
"""

from .engine import HybridTradingEngine
from .config import TradingConfig

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = ["HybridTradingEngine", "TradingConfig"]
