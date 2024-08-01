import os
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from utils.setup_driver import setup_driver


def scrape_page_new(driver, url):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all('tr', id='table-content')
    page_data = []
    for row in rows:
        columns = row.find_all('td')
        title = columns[1].find('a').text
        title_url = columns[1].find('a')['href']
        description = columns[2].text.strip()
        regulation_number = extract_nomor_regulasi(title)
        web_url = url
        page_data.append([title, title_url, description, regulation_number, web_url])
    return page_data

def extract_nomor_regulasi(title):
    patterns = [
        r'\bNomor\s+\d+/\d+/PBI/\d+\b',
        r'\bNomor\s+\d+\s+Tahun\s+\d+\b',
        r'\bNomor\s+\d+\s+Tahun\s+\d+\s+tentang\b',
        r'\bPBI\s+\d+/\d+\b',
        r'\bUndang-undang\s+Nomor\s+\d+\s+Tahun\s+\d+\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, title)
        print(match)
        if match:
            return match.group()
    return "Nomor regulasi not found"

def scrape_all_pages_new():
    driver = setup_driver()
    urls = ['/id/kanal/perbankan/regulasi/surat-edaran-bank-indonesia/default.aspx', '/id/kanal/perbankan/regulasi/undang-undang/default.aspx',
            '/id/kanal/perbankan/regulasi/peraturan-bank-indonesia/default.aspx', '/id/kanal/perbankan/Regulasi/peraturan-ojk/Default.aspx', '/id/kanal/perbankan/Regulasi/surat-edaran-ojk/Default.aspx', '/id/kanal/syariah/regulasi/peraturan-perbankan-syariah-pbi-dan-sebi/Default.aspx', '/id/kanal/syariah/regulasi/undang-undang/Default.aspx']

    base_url = "https://www.ojk.go.id"
    all_data = []

    for url in urls:
        driver.get(base_url + url)

        all_data.extend(scrape_page_new(driver, base_url + url))
        print("Page 1 successfully scraped.")

        i = 2
        while True:
            try:
                next_page_text = str(i)
                pagination_container = driver.find_element(
                    By.ID, 'ctl00_PlaceHolderMain_ctl00_DataPagerArticles')

                if i % 10 == 1 and i >= 10:
                    if i > 11:
                        next_page_link = pagination_container.find_element(
                            By.XPATH, f'//a[@href="javascript:__doPostBack(\'ctl00$PlaceHolderMain$ctl00$DataPagerArticles$ctl01$ctl11\',\'\')"]')
                    else:
                        next_page_link = pagination_container.find_element(
                            By.XPATH, f'//a[@href="javascript:__doPostBack(\'ctl00$PlaceHolderMain$ctl00$DataPagerArticles$ctl01$ctl10\',\'\')"]')
                else:
                    next_page_link = pagination_container.find_element(
                        By.LINK_TEXT, next_page_text)

                driver.execute_script("arguments[0].click();", next_page_link)

                all_data.extend(scrape_page_new(driver, base_url + url))
                print(f"Page {i} successfully scraped.")

                i += 1
            except Exception as e:
                print('No more pages to scrape.')
                break

    df = pd.DataFrame(all_data, columns=['Title', 'URL', 'Description', 'Regulation Number', 'Web URL'])

    for index, row in df.iterrows():
        driver.get(base_url + row['URL'])
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body')
        if body.text.strip() == '':
            df.at[index, 'status'] = 'Need to sign in'
        else:
            df.at[index, 'status'] = 'Success'

        print(f"Checked {index + 1} out of {len(df)} rows.")

    driver.quit()

    # create csv folder if not exists
    if not os.path.exists('./log'):
        os.makedirs('./log')

    df.to_csv('./log/ojk_table_scraping_result_new.csv', index=False)
    print("Data has been scraped and saved to ojk_table_scraping_result_new.csv")
