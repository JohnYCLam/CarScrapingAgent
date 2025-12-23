from __future__ import annotations

from typing import Dict

from car_agent.scraping.constants import DRIVE_SEARCH_BASE, STATE_MAP


def build_drive_url(criteria: Dict) -> str:
    state_raw = (criteria.get("location") or "").lower()
    state = STATE_MAP.get(state_raw, "vic")

    listing_type = (criteria.get("listing_type") or "all").strip().lower()

    make = (criteria.get("make") or "").lower().replace(" ", "-")
    model = (criteria.get("model") or "").lower().replace(" ", "-")

    if make:
        if model:
            path = f"{listing_type}/{state}/all/{make}/{model}/"
        else:
            path = f"{listing_type}/{state}/all/{make}/"
    else:
        path = f"{listing_type}/{state}/"

    url = f"{DRIVE_SEARCH_BASE}{path}"

    hash_parts = []
    year_min = criteria.get("year_min")
    year_max = criteria.get("year_max")
    if year_min or year_max:
        hash_parts.append(f"year=[{year_min or 0},{year_max or 0}]")

    price_min = criteria.get("price_min", 0)
    price_max = criteria.get("price_max", 0)
    if price_min or price_max:
        hash_parts.append(f"price=[{price_min},{price_max}]")

    transmission = criteria.get("transmission")
    if transmission and transmission.lower() in ("auto", "automatic"):
        hash_parts.append("transmission=auto")

    mileage_max = criteria.get("mileage_max")
    if mileage_max:
        hash_parts.append(f"kms=[0,{mileage_max}]")

    hash_parts.append("sortBy=recommended")

    if hash_parts:
        url += "#" + "&".join(hash_parts)

    return url
