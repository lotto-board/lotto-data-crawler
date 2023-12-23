from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from config import FIRST_PLACE_PATH, SECOND_PLACE_PATH, PAGINATION_LINK_PATH

import time
import re

def extract_first_place_table_data(table_element, round: int):
    tbody = table_element.find_element(By.TAG_NAME, "tbody")

    data = []
    for row in tbody.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            print("1등 당첨자가 없습니다. 회차: ", round)
            break
        cell_data = {
            "name": cells[1].text,
            "type": cells[2].text,
            "address": cells[3].text,
            "round": round,
            "retailer_id": extract_retailer_id(retailer_cell=cells[-1])
        }
        data.append(cell_data)

    return data

def extract_second_place_table_data(table_element, round: int):
    tbody = table_element.find_element(By.TAG_NAME, "tbody")

    data = []
    for row in tbody.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            print("2등 당첨자가 없습니다. 회차: ", round)
            break
        cell_data = {
            "name": cells[1].text,
            "address": cells[2].text,
            "round": round,
            "retailer_id": extract_retailer_id(retailer_cell=cells[-1])}
        data.append(cell_data)

    return data


def extract_all_data(driver, wait, round: int):
    data = {"first": [], "second": []}
    # Extracting data from the first table
    table_element1 = driver.find_element(By.XPATH, FIRST_PLACE_PATH)
    data["first"] += extract_first_place_table_data(table_element=table_element1, round=round)


    # Extracting data from the second table and click the pagination
    pagination_index = 0
    while True:
        try:
            pagination_links = driver.find_elements(By.XPATH, PAGINATION_LINK_PATH)

            if pagination_index >= len(pagination_links):
                break

            link = pagination_links[pagination_index]
            link.click()

            pagination_index += 1

            wait.until(EC.presence_of_all_elements_located((By.XPATH, SECOND_PLACE_PATH)))
            time.sleep(1)

            second_place_table = driver.find_element(By.XPATH, SECOND_PLACE_PATH)
            data["second"] += extract_second_place_table_data(table_element=second_place_table, round=round)
        except Exception as e:
            print(f"ERROR: {e}")
            break

    return data

def extract_retailer_id(retailer_cell):
    try:
        retailer_element = retailer_cell.find_element(By.TAG_NAME, "a")
        onclick_attribute = retailer_element.get_attribute("onclick")
        match = re.search(r"showMapPage\('(\d+)'\)", onclick_attribute)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"ERROR EXTRACT RETAILER ID!")
    return "NOT FOUND"

def extract(driver, wait, round):
    try:
        select_element = wait.until(EC.presence_of_element_located((By.ID, "drwNo")))
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "searchBtn")))

        select = Select(select_element)

        select.select_by_value(str(round))

        search_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, FIRST_PLACE_PATH)))

        data = extract_all_data(driver=driver, wait=wait, round=round)
        return data
    except Exception as e:
        print(f"ERROR: {e} 회차: {round}")
        return None