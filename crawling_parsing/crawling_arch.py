"""Daum, Naver, Bing"""

import time
import random
from typing import TypeVar
from collections import deque

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


from crawling_parsing.parsing import DaumNewsCrawlingParsingDrive
from crawling_parsing.selenium_utils import chrome_option_injection, page_scroll_moving


T = TypeVar("T")


class DaumMovingElementLocation(DaumNewsCrawlingParsingDrive):
    """다음 크롤링"""

    def __init__(self, target: str, count: int) -> None:
        """
        Args:
            target (str): 검색 타겟
            count (int): 얼마나 수집할껀지
        """
        self.url = f"https://search.daum.net/search?w=news&nil_search=btn&DA=NTB&enc=utf8&cluster=y&cluster_page=1&q={target}"
        self.driver: webdriver.Chrome = chrome_option_injection()
        self.count = count - 3

    def next_page_moving(self, index: int) -> T:
        xpath = f'//*[@id="dnsColl"]/div[2]/div/div/a[{index}]'
        news_box_type: T = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return news_box_type

    def glean_and_move(self, index: int) -> str | bool:
        page_scroll_moving(self.driver, int(random.uniform(500, 1000)))
        self.driver.implicitly_wait(random.uniform(5.0, 10.0))
        data = self.news_info_collect(self.driver.page_source)
        time.sleep(1)
        try:
            next_page_button: T = self.next_page_moving(index)
            next_page_button.click()
        except Exception as e:
            return data, False

        return data, True

    def page_news_data_glean(self) -> deque:
        self.driver.get(self.url)
        data = deque()

        for i in range(1, 3):
            news_data, success = self.glean_and_move(i)
            data.append(news_data)
            if not success:
                break

        if self.count > 3:
            while self.count:
                news_data, success = self.glean_and_move(3)
                self.count -= 1

                if not success:
                    break

        return data
