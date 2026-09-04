import sys

from tools.anakin_search import search_web


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "cybersecurity hiring trends 2026"

    print(f"Searching Anakin for: {query}\n")

    try:
        results = search_web(query)

        if not results:
            print("No results found.")
            return

        for i, result in enumerate(results, start=1):
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet}")

            if result.date:
                print(f"   Date: {result.date}")

            print()

    except ValueError as exc:
        print(f"CONFIGURATION ERROR: {exc}")

    except RuntimeError as exc:
        print(f"SEARCH ERROR: {exc}")


if __name__ == "__main__":
    main()