# collect.py
import os
import re
import sys
from datetime import datetime
from scraper import Scraper
from helper import load_sources, write_dataframe, clean_dataframe, clean_articles

if __name__ == "__main__":
    # Check if the correct number of arguments is provided; if not, use today's date
    if len(sys.argv) < 2:
        print("Usage: python collect.py <json_source_folder> [specific_date]")
        sys.exit(1)
    elif len(sys.argv) == 2:
        # If only the source folder is provided, use today's date in YYYYMMDD format
        json_source_folder = sys.argv[1]
        specific_date = datetime.today().strftime('%Y%m%d')
        print(f"No specific date provided. Using today's date: {specific_date}")
    else:
        json_source_folder = sys.argv[1]
        specific_date = sys.argv[2]

    if not os.path.isdir(json_source_folder):
        print(f"Error: {json_source_folder} is not a valid directory.")
        sys.exit(1)

    rss_feeds = load_sources(json_source_folder)

    scraper = Scraper(rss_feeds, specific_date)
    articles = scraper.scrape()

    df = write_dataframe(articles)
    df = clean_dataframe(df)
    df = clean_articles(df)

