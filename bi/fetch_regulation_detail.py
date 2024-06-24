import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils.constants import CHROMEDRIVER_PATH, DATA_DETAIL_PATH, DATA_FILE_PATH, REGULATIONS_PATH


# XPaths for the elements to be scraped
title_xpath = '//*[@id="ctl00_PlaceHolderMain_ctl02__ControlWrapper_RichHtmlField"]'
date_xpath = '//*[@id="layout-date"]'
type_of_reg_xpath = '//*[@id="layout-jenis-peraturan"]'
sector_xpath = '//*[@id="layout-sektor-peraturan"]'
attachment_xpath = '//*[@id="layout-lampiran"]/div/div[2]/div'


def scrape_regulation_details(driver, url):
    driver.get(url)
    
    details = {}

    try:
        details['title'] = driver.find_element(By.XPATH, title_xpath).text
        details['date'] = driver.find_element(By.XPATH, date_xpath).text
        details['type_of_regulation'] = driver.find_element(By.XPATH, type_of_reg_xpath).text
        details['sector'] = driver.find_element(By.XPATH, sector_xpath).text
    except Exception as e:
        print(f"Error fetching details from {url}: {e}")
        return None

    return details


def scrape_regulation_attachments(driver, url, title):
    driver.get(url)
    attachments = []

    try:
        attachment_section = driver.find_element(By.XPATH, attachment_xpath)
        attachment_elements = attachment_section.find_elements(By.XPATH, './/a')
        for attachment in attachment_elements:
            attachments.append({
                "title": title,
                "file_name": attachment.text,
                "file_link": attachment.get_attribute('href')
            })
    except Exception as e:
        print(f"Error fetching attachments from {url}: {e}")
    
    return attachments


def main():
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    df = pd.read_csv(REGULATIONS_PATH)
    data_detail = []
    data_file = []

    for link in df['link']:
        details = scrape_regulation_details(driver, link)
        if details:
            data_detail.append(details)
            attachments = scrape_regulation_attachments(driver, link, details['title'])
            data_file.extend(attachments)

    driver.quit()

    df_detail = pd.DataFrame(data_detail)
    df_detail.to_csv(DATA_DETAIL_PATH, index=False)

    df_file = pd.DataFrame(data_file)
    df_file.to_csv(DATA_FILE_PATH, index=False)

if __name__ == "__main__":
    main()
