import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL      = os.getenv("DATABASE_URL", "sqlite:///./idx_insights.db")
API_HOST          = os.getenv("API_HOST", "0.0.0.0")
API_PORT          = int(os.getenv("API_PORT", "8000"))

MORNING_CRON      = "0 7 * * 1-5"
EVENING_CRON      = "0 18 * * 1-5"
LOOKBACK_DAYS     = 250

ATR_PERIOD        = 14
ATR_TARGET_MULT   = 2.0
ATR_STOP_MULT     = 1.0
VOLUME_SPIKE_MULT = 1.5

SCORE_STRONG_BUY  = 5
SCORE_BUY         = 3
SCORE_SELL        = -3
SCORE_STRONG_SELL = -5
