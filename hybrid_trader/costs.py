"""Single, explicit transaction-cost model shared by live and backtest code."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class CostModel:
    commission_rate: float = 0.0
    sell_tax_rate: float = 0.0
    slippage_rate: float = 0.0
    fx_rate: float = 1.0

    def __post_init__(self) -> None:
        for name in ("commission_rate", "sell_tax_rate", "slippage_rate"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if not isfinite(self.fx_rate) or self.fx_rate <= 0:
            raise ValueError("fx_rate must be finite and positive")

    def estimate(self, side: str, notional: float) -> dict[str, float]:
        """Return explicit costs; caller must replace estimates with fills."""
        if not isfinite(notional) or notional < 0:
            raise ValueError("notional must be finite and non-negative")
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        commission = notional * self.commission_rate
        tax = notional * self.sell_tax_rate if side == "SELL" else 0.0
        slippage = notional * self.slippage_rate
        return {
            "commission": commission,
            "tax": tax,
            "slippage": slippage,
            "total": commission + tax + slippage,
            "base_notional": notional,
            "fx_rate": self.fx_rate,
        }

    def net_cash_delta(self, side: str, notional: float) -> float:
        costs = self.estimate(side, notional)
        return -(notional + costs["total"]) if side.upper() == "BUY" else notional - costs["total"]
