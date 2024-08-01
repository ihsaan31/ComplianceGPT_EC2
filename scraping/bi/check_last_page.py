from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.constants import CHROMEDRIVER_PATH


def navigate_to_last_page(web, executable_path):
    service = Service(executable_path=executable_path)
    driver = webdriver.Chrome(service=service)
    next_button_xpath = '//input[@class="next"]'
    
    driver.get(web)
    
    while True:
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            ActionChains(driver).click(next_button).perform()
            
            # Wait for the page to load by checking for staleness of the next button
            WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
        except:
            break  # Exit loop if next button is not found or clickable
    
    print("Reached the last page. You can now manually explore the page.")
    time.sleep(600)  # Pause for 10 minutes to allow manual exploration
    
    driver.quit()


if __name__ == "__main__":
    web = 'https://www.bi.go.id/en/publikasi/peraturan/Default.aspx'

    navigate_to_last_page(web, CHROMEDRIVER_PATH)
