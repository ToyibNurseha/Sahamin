from typing import List
import requests

_DEFAULT_TICKERS = [
    "AALI", "ACES", "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "ASII", "BBCA", "BBNI",
    "BBRI", "BBTN", "BMRI", "BRPT", "BUKA", "CPIN", "EXCL", "GGRM", "GOTO", "HMSP",
    "HRUM", "ICBP", "INCO", "INDF", "INKP", "INTP", "ITMG", "JSMR", "KLBF", "MAPI",
    "MDKA", "MEDC", "MIKA", "PGAS", "PTBA", "SMGR", "TKIM", "TLKM", "TOWR", "UNTR",
    "UNVR", "BSDE", "CTRA", "MYOR", "PWON", "SMRA", "ISAT", "SIDO", "ULTJ", "WIKA",
]

DEFAULT_SYMBOLS: List[str] = [f"{t}.JK" for t in _DEFAULT_TICKERS]


def fetch_all_idx_symbols() -> List[str]:
    try:
        resp = requests.get(
            "https://www.idx.co.id/primary/StockData/GetSecurities",
            params={"start": 0, "length": 1000, "type": "s"},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        codes = [
            item["Code"].strip()
            for item in data.get("data", [])
            if item.get("Code", "").strip()
        ]
        if not codes:
            raise ValueError("Empty code list returned")
        return [f"{code}.JK" for code in codes]
    except Exception as exc:
        print(f"[symbols] Failed to fetch IDX list ({exc}). Using {len(DEFAULT_SYMBOLS)} defaults.")
        return DEFAULT_SYMBOLS
