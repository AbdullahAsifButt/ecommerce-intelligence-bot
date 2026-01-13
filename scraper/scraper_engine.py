import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode


URLS_TO_SCRAPE = [
    "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    "https://webscraper.io/test-sites/e-commerce/allinone/phones/touch",
]


async def scrape_products():
    print("Starting Scraper Engine...")

    crawled_data = []

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS, css_selector=".thumbnail"  # Always get fresh data
    )

    async with AsyncWebCrawler() as crawler:
        for url in URLS_TO_SCRAPE:
            print(f"Scraping: {url}")

            result = await crawler.arun(url=url, config=config)

            if result.success:
                print(f"Found {len(result.markdown)} characters of data.")

                page_data = {
                    "url": url,
                    "content": result.markdown,  # The raw text of prices, names, reviews
                }
                crawled_data.append(page_data)
            else:
                print(f"❌ Failed to scrape {url} - Error: {result.error_message}")

    output_path = os.path.join("data", "products.json")

    os.makedirs("data", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(crawled_data, f, indent=2)

    print(f"\nData saved to {output_path}")
    print(f"Total Pages Scraped: {len(crawled_data)}")


if __name__ == "__main__":
    asyncio.run(scrape_products())
