from __future__ import annotations


class RiskManager:
    def __init__(self, risk_per_trade_pct: float, max_daily_loss_pct: float, stop_loss_pct: float):
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.stop_loss_pct = stop_loss_pct

    def position_size(self, capital: float, price: float) -> int:
        if price <= 0:
            return 0
        risk_amount = capital * (self.risk_per_trade_pct / 100)
        stop_distance = price * (self.stop_loss_pct / 100)
        if stop_distance <= 0:
            return 0
        qty = int(risk_amount // stop_distance)
        return max(1, qty)

    def exceeded_daily_loss(self, start_capital: float, current_capital: float) -> bool:
        if start_capital <= 0:
            return False
        drawdown_pct = ((start_capital - current_capital) / start_capital) * 100
        return drawdown_pct >= self.max_daily_loss_pct
