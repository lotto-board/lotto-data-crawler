from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base

import time

FIRST_PLACE_PATH = "//h4[contains(text(), '1등 배출점')]/ancestor::div[@class='group_content']/table[@class='tbl_data tbl_data_col']"
SECOND_PLACE_PATH = "//h4[contains(text(), '2등 배출점')]/ancestor::div[@class='group_content']/table[@class='tbl_data tbl_data_col']"

PAGINATION_LINK_PATH = "//div[@id='page_box']//a[not(contains(@class, 'current')) and not(contains(@href, '#'))]"

driver = webdriver.Chrome()

driver.get("https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645")
time.sleep(3)

wait = WebDriverWait(driver, 10)

database_url = ""
engine = create_engine(database_url)
Base = declarative_base()



class First(Base):
    __tablename__ = 'first_place'
    id = Column(Integer, Sequence('first_id_seq'), primary_key=True)
    name = Column(String)
    type = Column(String)
    address = Column(String)
    round = Column(Integer)

class Second(Base):
    __tablename__ = 'second_place'
    id = Column(Integer, Sequence('second_id_seq'), primary_key=True)
    name = Column(String)
    address = Column(String)
    round = Column(Integer)

def extract_first_place_table_data(table_element, round: int):
    tbody = table_element.find_element(By.TAG_NAME, "tbody")

    data = []
    for row in tbody.find_elements(By.TAG_NAME, "tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            print("1등 당첨자가 없습니다. 회차: ", round)
            break
        cell_data = {"name": cells[1].text, "type": cells[2].text, "address": cells[3].text, "round": round}
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
        cell_data = {"name": cells[1].text, "address": cells[2].text, "round": round}
        data.append(cell_data)

    return data


def extract_all_data(round: int):
    data = {"first": [], "second": []}
    # Extracting data from the first table
    table_element1 = driver.find_element(By.XPATH, FIRST_PLACE_PATH)
    data["first"] += extract_first_place_table_data(table_element=table_element1, round=round)


    # Extracting data from the second table and click the pagination
    pagination_index = 0
    while True:
        try:
            pagination_links = driver.find_elements(By.XPATH, "//div[@id='page_box']//a")

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

def insert_data(data):
    Session = sessionmaker(bind=engine)
    session = Session()
    for item in data['first']:
        record = First(name=item['name'], type=item['type'], address=item['address'], round=item['round'])
        session.add(record)
    
    for item in data['second']:
        record = Second(name=item['name'], address=item['address'], round=item['round'])
        session.add(record)

    session.commit()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    for option_value in range(987, 0, -1):
        try:
            select_element = wait.until(EC.presence_of_element_located((By.ID, "drwNo")))
            search_button = wait.until(EC.element_to_be_clickable((By.ID, "searchBtn")))

            select = Select(select_element)

            select.select_by_value(str(option_value))

            search_button.click()

            wait.until(EC.presence_of_element_located((By.XPATH, FIRST_PLACE_PATH)))

            data = extract_all_data(option_value)

            insert_data(data)

            time.sleep(2)
        except Exception as e:
            print(f"ERROR: {e} 회차: {option_value}")
            break
