from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementNotInteractableException


# Path to your WebDriver executable
webdriver_path = r'c:\Users\san\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)

# Open the URL
url = 'https://sikepo.ojk.go.id/SIKEPO/SkemaKodifikasi?objek=59836259-42bf-4bb7-b111-d13e51592e04'
driver.get(url)
# Wait for the tree view element to be present
treeview_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="simple-treeview"]'))
)

# Function to expand all nodes within the tree view element
def open_all_navbar(driver):
    num_leaves = 4
    i = 0
    while i < num_leaves:
        try:
            # Wait until the elements are present
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".dx-treeview-toggle-item-visibility:not(.dx-treeview-toggle-item-visibility-opened)"))
            )
            if len(elements) == 0:
                break
            
            # Iterate through and click each element
            for element in elements:
                try:
                    # Scroll to the element if necessary
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    driver.execute_script("arguments[0].click();", element)
                except Exception as e:
                    print(f"Could not click the element: {e}")
            i += 1
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Success")

open_all_navbar(driver)

# Function to parse the tree structure
def parse_tree(node):
    tree = {}
    for child in node.find_all('li', recursive=False):
        label = child.get('aria-label')
        item_id = child.get('data-item-id')
        subtree = child.find('ul')
        if subtree:
            tree[label] = {
                'data-item-id': item_id,
                'children': parse_tree(subtree)
            }
        else:
            tree[label] = {
                'data-item-id': item_id,
                'children': {}
            }
    return tree

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
root_node = soup.find('ul', class_='dx-treeview-node-container')
tree_structure = parse_tree(root_node)

# Function to click all items in the tree, starting with the deepest
def click_items(driver, tree):
    for key, value in tree.items():
        # Recursively click children first
        if 'children' in value and value['children']:
            click_items(driver, value['children'])
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
            print("length row of {data_item_id} is ", len(rows))
            # print(rows)
            
            for row in rows:
                try:
            # Find the link with class 'btn-action-ojk linkketentuanterkait'
                    link = WebDriverWait(row, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//a[@class='btn-action-ojk linkketentuanterkait']"))
                    )
                    url = link.get_attribute("href")
                    driver.execute_script("window.open(arguments[0], '_blank');", url)
                    
                    time.sleep(0.5)
                    driver.switch_to.window(driver.window_handles[-1])
                    try:
                         href_element = WebDriverWait(driver, 3).until(
                         EC.presence_of_element_located((By.XPATH, "//a[text()='Export to PDF']")))
                         driver.execute_script("arguments[0].click();", href_element)
                         driver.close()
                    except TimeoutException:
                         print("Timeout occurred while waiting for 'Export to PDF' link. Skipping...")
                         driver.close()
                    finally:
                         driver.switch_to.window(driver.window_handles[0])
                    time.sleep(0.5)

                    link = WebDriverWait(row, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//a[@class='btn-action-ojk linkrekamjejak']"))
                    )
                    url = link.get_attribute("href")
                    driver.execute_script("window.open(arguments[0], '_blank');", url)
                    
                    time.sleep(0.5)
                    driver.switch_to.window(driver.window_handles[-1])
                    try:
                         href_element = WebDriverWait(driver, 3).until(
                         EC.presence_of_element_located((By.XPATH, "//a[text()='Export to PDF']")))
                         driver.execute_script("arguments[0].click();", href_element)
                         driver.close()
                    except TimeoutException:
                         print("Timeout occurred while waiting for 'Export to PDF' link. Skipping...")
                         driver.close()
                    finally:
                         driver.switch_to.window(driver.window_handles[0])
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Exception occurred while processing row: {str(e)}")
                    continue


        except TimeoutException:
                    print(f"Timeout occurred while interacting with view options for {data_item_id}, skipping...")
        except Exception as e:
                    print(f"An error occurred while interacting with view options: {e}")

click_items(driver, tree_structure)
