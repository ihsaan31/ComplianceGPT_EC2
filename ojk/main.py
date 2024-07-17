from utils.check_ocr import add_ocr_column_to_csv, copy_scanned_pdfs, list_scanned_pdfs
from utils.filename_sanitizer import sanitize_filenames
from utils.new_filename_sanitizer import sanitize_filenames_new
from utils.table_scraper import scrape_all_pages
from utils.new_table_scraper import scrape_all_pages_new
from utils.document_scraper import download_documents
from utils.new_document_scraper import download_documents_new
from utils.zip_processor import process_zip_files
import pandas as pd
import os
import time


def main():
    # # Scrape all pages
    # print("Starting to scrape all pages...")
    # scrape_all_pages_new()
    # print("Scraping of all pages completed.")

    # Download documents
    # print("Starting to download documents...")

    # while not os.path.exists('./log/ojk_table_scraping_result.csv'):
    #     time.sleep(1)

    # df = pd.read_csv('./log/ojk_table_scraping_result_new.csv')
    # download_documents_new(df)
    # print("Downloading of documents completed.")

    # Extract zip files
    # df_zip = pd.read_csv('./log/ojk_document_scraping_result_new_backup.csv')
    # print("Starting to extract zip files...")
    # process_zip_files(df_zip)
    # print("Extraction of zip files completed.")

    # change filename
    print("Changing filename...")
    sanitize_filenames_new()
    print("Changing filename completed.")

    # print("Scanned PDF files:")
    # add_ocr_column_to_csv()
    # copy_scanned_pdfs()
    


if __name__ == "__main__":
    main()
