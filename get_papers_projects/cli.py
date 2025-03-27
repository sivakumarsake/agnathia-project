import argparse
from typing import Optional
from paper_fetcher import PaperFetcher

def main() -> None:
    """Command-line interface for fetching PubMed papers."""
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with non-academic affiliations.")
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--file", help="Output CSV filename")
    args = parser.parse_args()

    fetcher = PaperFetcher(args.query, args.debug)
    try:
        ids = fetcher.fetch_paper_ids()
        papers = fetcher.fetch_paper_details(ids)
        fetcher.save_to_csv(papers, args.file)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()