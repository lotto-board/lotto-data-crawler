from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from models import First, Second, ShopInfo, Session, WinningShop  # 클래스 임포트
from scraper import extract, extract_shop_info, update_latlng  # 스크래핑 함수 임포트
from config import LOTTO_WINNING_SHOP_URL

import time


# NOTE: 매장 정보 업데이트 메소드
def shop_info(driver, wait):
    session = Session()
    ids = ShopInfo.select_all_if_null(session=session)
    for (shop_id, ) in ids:
        data = extract_shop_info(driver, wait, shop_id)
        ShopInfo.update(session=session, retailer_id=shop_id, data=data)
        time.sleep(0.5)


# NOTE: 특정 회차 데잍터 수집
def get_round(driver, wait, number_of_round):
    data = extract(driver=driver, wait=wait, number_of_round=number_of_round)
    print(f"EXTRACTED DATA: {data}")
    if data:
        First.insert(data['first'])
        Second.insert(data['second'])
        get_shop_detail(driver=driver, wait=wait, data=data['first'], is_first=True)
        get_shop_detail(driver=driver, wait=wait, data=data['second'], is_first=False)


def get_shop_detail(driver, wait, data, is_first):
    session = Session()
    for shop in data:
        retailer_id = shop['retailer_id']
        is_exist = ShopInfo.is_exist(session=session, retailer_id=retailer_id)
        print(f"RETAILER_ID: {retailer_id} - IS_EXIST: {is_exist}")
        if not is_exist:
            shop_detail = extract_shop_info(driver=driver, wait=wait, shop_id=retailer_id)
            ShopInfo.insert(session=session, data=shop_detail)
        WinningShop.upsert_record(session=session, retailer_id=retailer_id, is_first=is_first)
    session.commit()


# NOTE: round 범위 당첨점 수집
def get_all_round(driver, wait, start, end):
    driver.get(LOTTO_WINNING_SHOP_URL)
    for number_of_round in range(start, end, -1):
        get_round(driver=driver, wait=wait, number_of_round=number_of_round)
        time.sleep(2)


# NOTE: 초기 shop table 정보를 삽입 하기 위한 메소드
def update_geoinfo(driver, wait):
    session = Session()
    shops = session.query(ShopInfo).all()

    for shop in shops:
        result = update_latlng(driver, wait, shop.retailer_id)

        if result:
            print("Address: " + shop.address + " longitude: " + result['longitude'] + " latitude: " + result['latitude'])
            shop.latitude = result["latitude"]
            shop.longitude = result["longitude"]
            session.add(shop)
        else:
            print(f"ERROR! Address: {shop.address}")
            break
        time.sleep(0.5)
    session.commit()


def main():
    options = Options()
    options.add_argument("--window-size=1200,900")
    options.add_argument("--headless")  # Enables headless mode
    
    driver = webdriver.Chrome(options=options)
    driver.get(LOTTO_WINNING_SHOP_URL)
    time.sleep(3)

    wait = WebDriverWait(driver, 10)

    get_round(driver=driver, wait=wait, number_of_round=1101)
    

if __name__ == "__main__":
    main()
