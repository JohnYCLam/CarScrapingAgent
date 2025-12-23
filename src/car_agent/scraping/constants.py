from __future__ import annotations

# State mapping for Drive URL builder
STATE_MAP = {
    "new south wales": "nsw", "nsw": "nsw",
    "victoria": "vic", "vic": "vic",
    "queensland": "qld", "qld": "qld",
    "south australia": "sa", "sa": "sa",
    "western australia": "wa", "wa": "wa",
    "tasmania": "tas", "tas": "tas",
    "australian capital territory": "act", "act": "act",
    "northern territory": "nt", "nt": "nt",
}

# Shared request headers for Drive scraping
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Optional: commonly used base URL
DRIVE_BASE_URL = "https://www.drive.com.au"
DRIVE_SEARCH_BASE = f"{DRIVE_BASE_URL}/cars-for-sale/search/"

# Optional: hard limits to keep things safe
MAX_SNIPPET_CHARS = 1500
REQUEST_TIMEOUT_S = 15
DEFAULT_POLITE_SLEEP_S = 1.0
