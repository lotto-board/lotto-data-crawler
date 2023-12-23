from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from models import First, Second  # 클래스 임포트
from scraper import extract  # 스크래핑 함수 임포트

import time


def main():
    driver = webdriver.Chrome()

    driver.get("https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645")
    time.sleep(3)

    wait = WebDriverWait(driver, 10)
    start_round = 1098
    end_round = 1097
    for option_value in range(start_round, end_round, -1):
        data = extract(driver=driver, wait=wait, round=option_value)
        if data:    
            First.insert(data['first'])
            Second.insert(data['second'])
        time.sleep(2)

if __name__ == "__main__":
    main()
