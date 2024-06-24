from utils.table_scraper import scrape_all_pages
from utils.document_scraper import download_documents
import pandas as pd
import os
import time


def main():
    # Scrape all pages
    print("Starting to scrape all pages...")
    scrape_all_pages()
    print("Scraping of all pages completed.")

    # Download documents
    print("Starting to download documents...")

    while not os.path.exists('./log/ojk_table_scraping_result.csv'):
        time.sleep(1)

    df = pd.read_csv('./log/ojk_table_scraping_result.csv')
    download_documents(df)
    print("Downloading of documents completed.")


if __name__ == "__main__":
    main()
