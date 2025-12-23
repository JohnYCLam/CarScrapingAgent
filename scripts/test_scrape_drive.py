from car_agent.config import Settings
from car_agent.llm.client import build_llm
from car_agent.scraping.drive_scraper import scrape_drive

def main():
    settings = Settings()
    llm = build_llm(settings)

    criteria = {'make': 'Mazda', 'model': 'CX-3', 'listing_type': 'used', 'year_min': 2020, 'price_max': 25000, 'location': 'Victoria'}
    results = scrape_drive(criteria, llm=llm, max_results=30, max_page=1)

    print("count =", len(results))
    for r in results[:5]:
        print(r)

if __name__ == "__main__":
    main()
