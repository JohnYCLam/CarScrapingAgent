from __future__ import annotations

import re
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from car_agent.scraping.constants import DEFAULT_HEADERS, DRIVE_BASE_URL, REQUEST_TIMEOUT_S, DEFAULT_POLITE_SLEEP_S
from car_agent.scraping.drive_url import build_drive_url
from car_agent.scraping.filters import extract_year, filter_snippet_by_criteria
from car_agent.scraping.llm_parser import parse_listings_with_llm


def scrape_drive(criteria: Dict, llm, max_results: int = 20, max_page: int = 1):
    """Fixed: deduplicate + detail page scraping"""
    
    # Step 1: Get unique listing URLs from search
    listing_urls = get_unique_listing_urls(criteria, max_page)
    print(f"[SCRAPE] Found {len(listing_urls)} unique URLs")
    
    # Step 2: Scrape each detail page (accurate data)
    results = []
    seen_cars = set()  # Deduplicate by URL
    
    for i, url in enumerate(listing_urls[:max_results]):
        if url in seen_cars:
            continue
            
        try:
            print(f"[SCRAPE] Detail #{i+1}/{len(listing_urls)}: {url}")
            car_data = scrape_detail_page(url)
            
            if car_data and matches_criteria(car_data, criteria):
                results.append(car_data)
                seen_cars.add(url)
                print(f"[SCRAPE] ✅ {car_data['name']} ${car_data['price']:,} ({car_data['mileage']:,}km)")
            time.sleep(1)  # Polite delay
            
        except Exception as e:
            print(f"[SCRAPE] ❌ {url}: {e}")
            continue
    
    print(f"[SCRAPE] Final: {len(results)} results")
    return results

def get_unique_listing_urls(criteria: Dict, max_page: int) -> List[str]:
    """Extract UNIQUE listing URLs from search pages"""
    all_urls = set()
    base_url = build_drive_url(criteria)
    
    for page in range(1, max_page + 1):
        url = f"{base_url}page={page}"
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Find listing links
        cards = soup.find_all('div', class_=lambda x: x and (
            'listing-card' in x or 'marketplace-listing-card' in x
        ))
        
        for card in cards:
            link = card.find('a', href=True)
            if link and '/cars-for-sale/car/' in link['href']:
                full_url = DRIVE_BASE_URL + link['href'].split('?')[0]  # Clean URL
                all_urls.add(full_url)
    
    return list(all_urls)

def scrape_detail_page(url: str) -> Dict:
    """Accurate data from INDIVIDUAL detail page"""
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
    soup = BeautifulSoup(resp.text, 'lxml')
    
    # Title
    title_el = soup.find('h1') or soup.find('title')
    name = title_el.get_text(strip=True) if title_el else "Unknown"
    
    # Price (multiple selectors)
    price_selectors = [
        '[data-testid="price"]', '.price', '.listing-price',
        'span:contains("$")', '[class*="price"]'
    ]
    price_text = ""
    for selector in price_selectors:
        el = soup.select_one(selector)
        if el:
            price_text = el.get_text(strip=True)
            break
    
    price = parse_price(price_text)
    year = extract_year_from_title(name)
    mileage = parse_mileage(soup)
    location = parse_location(soup)
    
    return {
        "name": name,
        "price": price,
        "year": year,
        "mileage": mileage or 0,
        "location": location or "VIC",
        "url": url,
        "source": "drive.com.au"
    }

def parse_price(text: str) -> int:
    """$26,470 → 26470"""
    import re
    match = re.search(r'[\$]?([\d,]+\.?\d*)', text.replace('k', '000'))
    return int(match.group(1).replace(',', '')) if match else 0

def extract_year_from_title(text: str) -> int:
    """2022 Mazda → 2022"""
    import re
    match = re.search(r'\b(20\d{2}|19\d{2})\b', text)
    return int(match.group(1)) if match else 0

def parse_mileage(soup: BeautifulSoup) -> int:
    """Find mileage from detail page"""
    import re
    
    # Try multiple selectors
    selectors = [
        '[data-testid="mileage"]', '.mileage', '[class*="km"]', '[class*="mileage"]'
    ]
    
    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            text = el.get_text()
            match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
            if match:
                return int(match.group(1).replace(',', ''))
    
    # Fallback: search entire page
    text = soup.get_text()
    match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*km', text, re.I)
    return int(match.group(1).replace(',', '')) if match else 0

def parse_location(soup: BeautifulSoup) -> str:
    """VIC, NSW, etc."""
    location_selectors = [
        '[data-testid="location"]', '.location', '[class*="location"]'
    ]
    for selector in location_selectors:
        el = soup.select_one(selector)
        if el:
            return el.get_text(strip=True).upper()
    return "VIC"

def matches_criteria(car: Dict, criteria: Dict) -> bool:
    """Post-scrape filtering"""
    if criteria.get('year_min') and car.get('year', 0) < criteria['year_min']:
        return False
    if criteria.get('price_max') and car.get('price', 0) > criteria['price_max']:
        return False
    return True