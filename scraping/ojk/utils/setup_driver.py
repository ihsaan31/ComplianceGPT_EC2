from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options


def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Menjalankan browser dalam mode headless
    # chrome_options.add_argument('--disable-extensions')  # Menonaktifkan ekstensi
    # chrome_options.add_argument('--disable-gpu')  # Menonaktifkan GPU
    # chrome_options.add_argument('--window-size=1920,1080')  # Mengatur ukuran jendela
    service = ChromeService(executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
