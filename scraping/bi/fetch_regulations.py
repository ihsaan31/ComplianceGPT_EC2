from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

from utils.constants import CHROMEDRIVER_PATH, REGULATIONS_PATH


# XPaths for the elements to be scraped
title_xpath = './/a[@class="mt-0 media__title ellipsis--two-line"]'
regulations_xpath = '//div[@class="media media--pers"]'
next_button_xpath = '//input[@class="next"]'


def process_regulations(regulations):
    data = []
    
    for regulation in regulations:
        title_element = regulation.find_element(By.XPATH, title_xpath)
        title_text = title_element.text.upper()
        title_link = title_element.get_attribute('href')
        data.append({"title": title_text, "link": title_link})

        print(title_text)
    
    return data


def scrape_regulations_to_csv(web, executable_path, output_csv):
    service = Service(executable_path=executable_path)
    driver = webdriver.Chrome(service=service)

    driver.get(web)
    
    all_data = []
    seen_regulations = set()
    
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, regulations_xpath))
        )
        
        regulations = driver.find_elements(By.XPATH, regulations_xpath)
        current_data = process_regulations(regulations)
        
        # Check for new regulations to avoid duplicates
        new_data = [item for item in current_data if item['link'] not in seen_regulations]
        if not new_data:
            break  # Exit if no new data is found
        
        all_data.extend(new_data)
        seen_regulations.update(item['link'] for item in new_data)
        
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            ActionChains(driver).click(next_button).perform()
            
            # Wait for new page to load by checking for new regulations
            WebDriverWait(driver, 10).until(
                EC.staleness_of(regulations[0])
            )
        except:
            break  # Exit loop if next button is not found or clickable
    
    driver.quit()
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    web = 'https://www.bi.go.id/en/publikasi/peraturan/Default.aspx'

    scrape_regulations_to_csv(web, CHROMEDRIVER_PATH, REGULATIONS_PATH)
