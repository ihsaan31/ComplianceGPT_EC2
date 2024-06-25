from util.functions import open_all_navbar, parse_tree, count_files, new_file
from util.constants import CHROMEDRIVER_PATH, FOLDER_BANK_UMUM_KONVENSIONAL, FOLDER_BANK_UMUM_SYARIAH, FOLDER_UNIT_USAHA_SYARIAH, FOLDER_BPR_KONVENSIONAL, FOLDER_BPR_SYARIAH
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementNotInteractableException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import time
import os
import glob


dic = {}
DOWNLOAD_FOLDER = ""


def fetch_data(section):
    global DOWNLOAD_FOLDER
    global dic

    try:
        if section == "Bank Umum Konvensional":
            DOWNLOAD_FOLDER = FOLDER_BANK_UMUM_KONVENSIONAL
            URL = "https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=134882C3-53DF-4E01-9F2F-F204FE0A7E7E"
        elif section == "Bank Umum Syariah":
            DOWNLOAD_FOLDER = FOLDER_BANK_UMUM_SYARIAH
            URL = "https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=59836259-42bf-4bb7-b111-d13e51592e04"
        elif section == "Unit Usaha Syariah":
            DOWNLOAD_FOLDER = FOLDER_UNIT_USAHA_SYARIAH
            URL = "https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=b4d40e63-1738-46b0-9416-dac6815385b4"
        elif section == "BPR Konvensional":
            DOWNLOAD_FOLDER = FOLDER_BPR_KONVENSIONAL
            URL = "https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=d0b36c3a-cbc1-45c7-9a06-cf1135d96d71"
        elif section == "BPR Syariah":
            DOWNLOAD_FOLDER = FOLDER_BPR_SYARIAH
            URL = "https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=af735e84-d2ad-46c8-a08b-61d45db9bcdc"
        else:
             raise AttributeError

    except:
        print("You can only fetch the following sections: 'Bank Umum Konvensional',  'Bank Umum Syariah', 'Unit Usaha Syariah', 'BPR Konvensional', 'BPR Syariah' ")
        return None
    
    # Ensure the download folder exists
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    chrome_options = Options()
    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_FOLDER),  
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Set up the Chrome WebDriver
    chrome_service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(URL)

    # Wait for the tree view element to be present
    treeview_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="simple-treeview"]'))
    )

    open_all_navbar(driver)

    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    root_node = soup.find('ul', class_='dx-treeview-node-container')
    tree_structure = parse_tree(root_node)

    try:
        click_items(driver, tree_structure)
    except Exception as e:
        print(f"An error occurred while navigating the Selenium: {e}")

    result = dic
    return result, tree_structure


# Function to click all items in the tree, starting with the deepest
def click_items(driver, tree):
    global dic
    global DOWNLOAD_FOLDER

    for key, value in tree.items():
        if len(dic) >= 2:
             break
        # Recursively click children first
        if 'children' in value and value['children']:
            click_items(driver, value['children'])
        else:
            if dic.get(key) != None:
                print("Key already found in dic")
                continue
            # Then click the current node
            data_item_id = value['data-item-id']
            element = driver.find_element(By.CSS_SELECTOR, f'[data-item-id="{data_item_id}"]')
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(1)

            # Interact with the view options
            try:
                view_optn = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="gridView_DXPagerBottom_PSI"]'))
                )
                view_optn.click()
                view_optn.send_keys(Keys.UP)
                view_optn.send_keys(Keys.ENTER)

                time.sleep(4)
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')    
                table = soup.find('table', {'id': 'gridView_DXMainTable'})

        # Extract table rows
                rows = driver.find_elements(By.CSS_SELECTOR, "tr.dxgvDataRow_Moderno")

                rows_table = table.find_all('tr', {'class': 'dxgvDataRow_Moderno'})
                i = 0
                data_list = []
                print("length row of {data_item_id} is ", len(rows))
                # print(rows)
                
                for row in rows:
                    try:
                # Find the link with class 'btn-action-ojk linkketentuanterkait'
                        cells = rows_table[i].find_all('td')

                        # Extract the cell data
                        jenis_ketentuan = cells[0].text.strip()
                        nomor_ketentuan = cells[1].text.strip()
                        tanggal_ketentuan = cells[2].text.strip()
                        judul_ketentuan = cells[3].text.strip()
                        link_dict = {}

                        cnt_files = count_files(DOWNLOAD_FOLDER)
                        link = WebDriverWait(row, 10).until(
                            EC.element_to_be_clickable((By.XPATH, ".//a[@class='btn-action-ojk linkketentuanterkait']"))
                        )
                        url = link.get_attribute("href")
                        driver.execute_script("window.open(arguments[0], '_blank');", url)
                        
                        time.sleep(0.5)
                        driver.switch_to.window(driver.window_handles[-1])
                        try:
                            href_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//a[text()='Export to PDF']")))
                            driver.execute_script("arguments[0].click();", href_element)
                            driver.close()
                        except TimeoutException:
                            print("Timeout occurred while waiting for 'Export to PDF' link. Skipping...")
                            driver.close()
                        finally:
                            driver.switch_to.window(driver.window_handles[0])
                        time.sleep(0.5)

                        link_ketentuan = new_file(cnt_files, DOWNLOAD_FOLDER)
                        link_dict["Ketentuan Terkait"] = link_ketentuan
                        time.sleep(0.5)


                        cnt_files = count_files(DOWNLOAD_FOLDER)
                        link = WebDriverWait(row, 10).until(
                            EC.element_to_be_clickable((By.XPATH, ".//a[@class='btn-action-ojk linkrekamjejak']"))
                        )
                        url = link.get_attribute("href")
                        driver.execute_script("window.open(arguments[0], '_blank');", url)
                        
                        time.sleep(0.5)
                        driver.switch_to.window(driver.window_handles[-1])
                        try:
                            href_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//a[text()='Export to PDF']")))
                            driver.execute_script("arguments[0].click();", href_element)
                            driver.close()
                        except TimeoutException:
                            print("Timeout occurred while waiting for 'Export to PDF' link. Skipping...")
                            driver.close()
                        finally:
                            driver.switch_to.window(driver.window_handles[0])
                        link_rekam = new_file(cnt_files, DOWNLOAD_FOLDER)
                        link_dict["Rekam Jejak"] = link_rekam
                        time.sleep(0.5)

                        row_data = {
                            'Jenis Ketentuan': jenis_ketentuan,
                            'Nomor Ketentuan': nomor_ketentuan,
                            'Tanggal Ketentuan': tanggal_ketentuan,
                            'Judul Ketentuan': judul_ketentuan,
                            'Links': link_dict
                        }
                        
                        # Append the dictionary to the list
                        data_list.append(row_data)
                        i += 1
                    except Exception as e:
                        print(f"Exception occurred while processing row: {str(e)}")
                        i += 1
                        continue

                dic[key] = data_list
            except TimeoutException:
                        print(f"Timeout occurred while interacting with view options for {data_item_id}, skipping...")
            except Exception as e:
                        print(f"An error occurred while interacting with view options: {e}")
        