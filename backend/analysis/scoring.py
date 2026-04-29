from typing import Tuple
from config import SCORE_STRONG_BUY, SCORE_BUY, SCORE_SELL, SCORE_STRONG_SELL, VOLUME_SPIKE_MULT


def score_indicators(ind: dict) -> Tuple[float, dict, str]:
    breakdown: dict = {}
    bb_pos: float = 0.5  # default: mid-band

    # ── RSI (±2) ──────────────────────────────────────────────────────────────
    rsi = ind.get("rsi")
    if rsi is not None:
        if rsi < 30:          rsi_score = 2
        elif rsi < 45:        rsi_score = 1
        elif rsi <= 55:       rsi_score = 0
        elif rsi <= 70:       rsi_score = -1
        else:                 rsi_score = -2
    else:
        rsi_score = 0
    breakdown["rsi"] = rsi_score

    # ── MACD histogram (±2) ───────────────────────────────────────────────────
    hist      = ind.get("macd_hist")
    hist_prev = ind.get("macd_hist_prev")
    if hist is not None:
        if hist > 0 and hist_prev is not None and hist > hist_prev:   macd_score = 2
        elif hist > 0:                                                  macd_score = 1
        elif hist < 0 and hist_prev is not None and hist < hist_prev: macd_score = -2
        elif hist < 0:                                                  macd_score = -1
        else:                                                           macd_score = 0
    else:
        macd_score = 0
    breakdown["macd"] = macd_score

    # ── EMA 20/50 cross (±1) ──────────────────────────────────────────────────
    ema20 = ind.get("ema20")
    ema50 = ind.get("ema50")
    if ema20 is not None and ema50 is not None:
        if ema20 > ema50:   ema_score = 1
        elif ema20 < ema50: ema_score = -1
        else:               ema_score = 0
    else:
        ema_score = 0
    breakdown["ema_cross"] = ema_score

    # ── Bollinger band position (±1) ──────────────────────────────────────────
    close    = ind.get("close")
    bb_upper = ind.get("bb_upper")
    bb_lower = ind.get("bb_lower")
    if close is not None and bb_upper is not None and bb_lower is not None:
        band_range = bb_upper - bb_lower
        if band_range > 0:
            bb_pos = (close - bb_lower) / band_range
            if bb_pos < 0.2:    bb_score = 1
            elif bb_pos > 0.8:  bb_score = -1
            else:               bb_score = 0
        else:
            bb_score = 0
    else:
        bb_score = 0
    breakdown["bollinger"] = bb_score

    # ── Stochastic (±1) ───────────────────────────────────────────────────────
    stoch_k = ind.get("stoch_k")
    stoch_d = ind.get("stoch_d")
    if stoch_k is not None and stoch_d is not None:
        if stoch_k < 20 and stoch_d < 20:   stoch_score = 1
        elif stoch_k > 80 and stoch_d > 80: stoch_score = -1
        else:                                stoch_score = 0
    else:
        stoch_score = 0
    breakdown["stochastic"] = stoch_score

    subtotal = rsi_score + macd_score + ema_score + bb_score + stoch_score

    # ── ADX amplifier (±0.5) ──────────────────────────────────────────────────
    adx = ind.get("adx")
    if adx is not None and adx > 25:
        if subtotal > 0:    adx_score = 0.5
        elif subtotal < 0:  adx_score = -0.5
        else:               adx_score = 0.0
    else:
        adx_score = 0.0
    breakdown["adx"] = adx_score

    # ── Volume spike amplifier (±0.5) ─────────────────────────────────────────
    vol_ratio = ind.get("vol_ratio")
    if vol_ratio is not None and vol_ratio > VOLUME_SPIKE_MULT:
        if subtotal > 0:    vol_score = 0.5
        elif subtotal < 0:  vol_score = -0.5
        else:               vol_score = 0.0
    else:
        vol_score = 0.0
    breakdown["volume"] = vol_score

    total = round(subtotal + adx_score + vol_score, 1)
    trade_type = _classify_trade(ind, total, bb_pos)
    return total, breakdown, trade_type


def _classify_trade(ind: dict, score: float, bb_pos: float) -> str:
    close     = ind.get("close")
    ema20     = ind.get("ema20")
    rsi       = ind.get("rsi")
    vol_ratio = ind.get("vol_ratio") or 0.0

    if score > 0:
        if rsi is not None and rsi < 40 and close is not None and ema20 is not None and close > ema20 * 0.97:
            return "PULLBACK"
        if bb_pos > 0.85 and vol_ratio > VOLUME_SPIKE_MULT:
            return "BREAKOUT"
        return "OVERSOLD_BOUNCE"
    if score < 0:
        if rsi is not None and rsi > 65:
            return "OVERBOUGHT_DROP"
        return "BREAKDOWN"
    return "NEUTRAL"


def label_from_score(score: float) -> str:
    if score >= SCORE_STRONG_BUY:   return "STRONG BUY"
    if score >= SCORE_BUY:          return "BUY"
    if score <= SCORE_STRONG_SELL:  return "STRONG SELL"
    if score <= SCORE_SELL:         return "SELL"
    return "HOLD"
