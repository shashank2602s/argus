import sys

from tools.anakin_scraper import scrape_urls


def main():
    urls = sys.argv[1:]

    if not urls:
        urls = ["https://example.com"]

    print(f"Scraping {len(urls)} URL(s)...\n")

    results = scrape_urls(urls)

    for result in results:
        print(f"URL: {result.url}")
        print(f"  Success: {result.success}")
        print(f"  Title: {result.title}")
        print(f"  Content length: {len(result.content)}")
        print(f"  Preview: {result.content[:300]}")

        if result.error:
            print(f"  Error: {result.error}")

        print()


if __name__ == "__main__":
    main()