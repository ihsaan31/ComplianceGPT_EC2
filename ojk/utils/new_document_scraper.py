import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
from utils.setup_driver import setup_driver

def href_to_filename(href):
    part1 = urllib.parse.unquote(href.split('/')[-2])
    part2 = urllib.parse.unquote(href.split('/')[-1])
    ext = os.path.splitext(part2)[1]
    part2 = os.path.splitext(part2)[0]
    max_name_length = 255 - len(ext) - 4  # 4 for the '--' separator
    length_part1 = len(part1)
    length_part2 = len(part2)
    if length_part2 > max_name_length:
        part2 = part2[:max_name_length - length_part1]
        return f"{part2}{ext}"
    if length_part1 + length_part2 > max_name_length:
        part1 = part1[:max_name_length - length_part2]
    return f"{part1} -- {part2}{ext}"


def download_document(url, path):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"404 Client Error: NOT FOUND for url: {url}")
            return False
        else:
            print(f"HTTP error occurred: {http_err}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False


def download_documents_new(df):
    driver = setup_driver()
    base_url = "https://www.ojk.go.id"
    paths = df[df['status'] == 'Success']['URL'].tolist()
    download_dir = './data_new'
    log_file = './log/download_progress_new.log'
    output_csv = './log/ojk_document_scraping_result_new.csv'
    document_data = []

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    start_index = 0
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            start_index = int(f.read().strip())

    # Load existing document data if the CSV file exists
    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        document_data = existing_df.values.tolist()

    for index in range(start_index, len(paths)):
        path = paths[index]
        # page_url = path
        page_url = base_url + path
        driver.get(page_url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.find('h1', class_='title-in').text.strip()
        tanggal_berlaku = soup.find(
            'div', id='ctl00_PlaceHolderMain_CommentModePanelArticleDateText').text.strip()
        
        links_div = ['ctl00_PlaceHolderMain_ctl04__ControlWrapper_RichHtmlField', 'ctl00_PlaceHolderMain_ctl05__ControlWrapper_RichHtmlField', 'ctl00_PlaceHolderMain_ctl09__ControlWrapper_RichHtmlField']
        document_links = []

        for link_div in links_div:
            document_links_div = soup.find('div', id=link_div)
            if document_links_div is not None:
                document_links.extend(document_links_div.find_all('a'))
            
        for link in document_links:
            if 'href' in link.attrs:
                filename = href_to_filename(link['href'])
                checked_text_value = link.text.strip()
                altlink = link['href']
                file_url = base_url + altlink

                if checked_text_value:
                    document_path = os.path.join(download_dir, filename)
                    success = download_document(file_url, document_path)
                    if not success:
                        retry_count = 3
                        for attempt in range(retry_count):
                            print(
                                f"Retrying {file_url} (Attempt {attempt + 1}/{retry_count})")
                            success = download_document(
                                file_url, document_path)
                            if success:
                                break

                    if success:
                        document_data.append([title, page_url, tanggal_berlaku, filename, file_url])

        # Save progress to log file
        with open(log_file, 'w') as f:
            f.write(str(index + 1))

        # Save document data to CSV incrementally
        document_df = pd.DataFrame(document_data, columns=[
            'title', 'page_url', 'tanggal_berlaku', 'filename', 'file_url'])
        document_df.to_csv(output_csv, index=False)

        print(f"Scraped {index + 1} out of {len(paths)} rows")

    driver.quit()
    print("Document data has been scraped, downloaded, and saved to ojk_document_scraping_result.csv")
