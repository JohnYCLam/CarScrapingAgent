from __future__ import annotations

import re
from typing import Optional


def extract_year(text: str) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group(0)) if m else None


def filter_snippet_by_criteria(snippet: str, criteria: dict) -> bool:
    year_min = criteria.get("year_min")
    if year_min:
        years_found = re.findall(r"\b19\d{2}\b|\b20\d{2}\b", snippet)
        if not years_found:
            return False
        years = [int(y) for y in years_found]
        if not any(y >= year_min for y in years):
            return False

    price_max = criteria.get("price_max")
    if price_max:
        prices_found = re.findall(r"\$\s?([\d,]+)", snippet)
        if not prices_found:
            prices_found = re.findall(r"\b\d{4,6}\b", snippet)
        if prices_found:
            prices = [int(p.replace(",", "")) for p in prices_found]
            if all(p > price_max for p in prices):
                return False

    return True
