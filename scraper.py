from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from config import *

import time
import re


def extract_first_place_table_data(table_element, number_of_round: int):
    tbody = table_element.find_element(By.TAG_NAME, "tbody")

    data = []
    for row in tbody.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            print("1등 당첨자가 없습니다. 회차: ", number_of_round)
            break

        cell_data = {
            "name": cells[1].text,
            "type": cells[2].text,
            "address": cells[3].text,
            "round": number_of_round,
            "retailer_id": extract_retailer_id(retailer_cell=cells[-1])
        }
        data.append(cell_data)

    return data


def extract_second_place_table_data(table_element, number_of_round: int):
    tbody = table_element.find_element(By.TAG_NAME, "tbody")

    data = []
    for row in tbody.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            print("2등 당첨자가 없습니다. 회차: ", number_of_round)
            break
        cell_data = {
            "name": cells[1].text,
            "address": cells[2].text,
            "round": number_of_round,
            "retailer_id": extract_retailer_id(retailer_cell=cells[-1])}
        data.append(cell_data)

    return data


def extract_all_data(driver, wait, number_of_round: int):
    data = {"first": [], "second": []}
    # Extracting data from the first table
    table_element1 = driver.find_element(By.XPATH, FIRST_PLACE_PATH)
    data["first"] += extract_first_place_table_data(table_element=table_element1, number_of_round=number_of_round)

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
            data["second"] += extract_second_place_table_data(table_element=second_place_table, number_of_round=number_of_round)
        except Exception as e:
            driver.save_screenshot('./screenshot.png')
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


def extract(driver, wait, number_of_round):
    try:
        select_element = wait.until(EC.presence_of_element_located((By.ID, "drwNo")))
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "searchBtn")))

        select = Select(select_element)

        select.select_by_value(str(number_of_round))

        search_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, FIRST_PLACE_PATH)))

        data = extract_all_data(driver=driver, wait=wait, number_of_round=number_of_round)
        return data
    except Exception as e:
        print(f"ERROR: {e} 회차: {number_of_round}")
        return None


def extract_shop_info(driver, wait, shop_id):
    try:
        driver.get(LOTTO_SHOP_DETAILS_URL + shop_id)
        wait.until(EC.presence_of_element_located((By.XPATH, ADDRESS)))
        table_element = driver.find_element(By.XPATH, ADDRESS)
        tbody = table_element.find_element(By.TAG_NAME, "tbody")
        tr_elements = tbody.find_elements(By.TAG_NAME, "tr")

        name = tr_elements[0].find_element(By.TAG_NAME, "td").text
        phone_number = tr_elements[1].find_element(By.TAG_NAME, "td").text
        address = tr_elements[2].find_element(By.TAG_NAME, "td").text
        latitude = driver.find_element(By.XPATH, LATITUDE).get_attribute("value")
        longitude = driver.find_element(By.XPATH, LONGITUDE).get_attribute("value")

        return {
            "retailer_id": shop_id,
            "name": name,
            "phone_number": phone_number,
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    

def update_latlng(driver, wait, shop_id):
    try:
        driver.get(LOTTO_SHOP_DETAILS_URL + shop_id)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, LATITUDE)))

        latitude = driver.find_element(By.XPATH, LATITUDE).get_attribute('value')
        longitude = driver.find_element(By.XPATH, LONGITUDE).get_attribute('value')

        return {
            "longitude": longitude,
            "latitude": latitude
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return None
