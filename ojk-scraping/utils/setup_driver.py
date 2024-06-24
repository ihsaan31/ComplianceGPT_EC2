from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options


def setup_driver():
    chrome_options = Options()
    service = ChromeService(executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
