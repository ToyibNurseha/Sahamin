from typing import Optional
from config import ATR_TARGET_MULT, ATR_STOP_MULT


def calculate_projection(ind: dict, signal_label: str) -> Optional[dict]:
    if signal_label == "HOLD":
        return None

    atr   = ind.get("atr")
    close = ind.get("close")
    if not atr or not close or atr <= 0:
        return None

    entry = round(close, 0)

    if signal_label in ("BUY", "STRONG BUY"):
        target    = round(entry + ATR_TARGET_MULT * atr, 0)
        stop_loss = round(entry - ATR_STOP_MULT  * atr, 0)
    else:  # SELL / STRONG SELL
        target    = round(entry - ATR_TARGET_MULT * atr, 0)
        stop_loss = round(entry + ATR_STOP_MULT  * atr, 0)

    risk   = abs(entry - stop_loss)
    reward = abs(target - entry)
    rr     = round(reward / risk, 2) if risk > 0 else 0.0

    return {
        "entry":       float(entry),
        "target":      float(target),
        "stop_loss":   float(stop_loss),
        "risk_reward": rr,
    }
