"""Daum, Naver, Bing"""

import time
import random
from typing import TypeVar, Any, Callable, Deque
from collections import deque

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
)

from crawling_parsing.parsing import (
    DaumNewsCrawlingParsingDrive,
    GoogleNewsCrawlingParsingDrive,
)
from crawling_parsing.selenium_utils import chrome_option_injection, page_scroll_moving


T = TypeVar("T")
WAIT_TIME = 5
UrlCollect = Deque[list[str]]


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
        page_scroll_moving(self.driver, int(random.uniform(30, 80)))
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


class GoogleMovingElementsLocation(GoogleNewsCrawlingParsingDrive):
    """구글 홈페이지 크롤링

    Args:
        GoogleNewsCrawlingParsingDrive (class): parsingDrive
    """

    def __init__(self, target: str, count: int) -> None:
        """
        Args:
            target (str): 검색 타겟
            count (int): 얼마나 수집할껀지
        """
        self.url = f"https://www.google.com/search?q={target}&tbm=nws&gl=ko&hl=kr"
        self.driver: webdriver.Chrome = chrome_option_injection()
        self.count = count

    def search_box_page_type(self, xpath: str) -> Any:
        """xpath 요소 찾기"""
        news_box_type: Any = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return news_box_type

    def a_loop_page(self, start: int, xpath_type: Callable[[int], str]) -> UrlCollect:
        """페이지 수집하면서 이동

        Args:
            start (int): 페이지 이동 시작 html location
            xpath_type (Callable[[int], str]): google은 여러 HTML 이므로 회피 목적으로 xpath 함수를 만듬
        """
        data = deque()
        try:
            for i in range(start, self.count + start):
                next_page_button: Any = self.search_box_page_type(xpath_type(i))
                print(f"{i-1}page로 이동합니다 --> {xpath_type(i)} 이용합니다")
                url_data: list[str] = self.news_info_collect(self.driver.page_source)
                data.append(url_data)
                next_page_button.click()
                self.driver.implicitly_wait(random.uniform(5.0, 10.0))
                page_scroll_moving(self.driver, int(random.uniform(1, 10)))
            else:
                print("google 수집 종료")
                self.driver.quit()
        except NoSuchElementException as e:
            print(f"요소를 찾을 수 없어 수집을 다시 시도합니다 --> {e}")
            self.driver.refresh()
        except WebDriverException as e:
            print(f"드라이버 이슈로 인해 수집을 중단합니다 --> {e}")
            self.driver.quit()
        return data

    def next_page_moving(self) -> UrlCollect:
        """페이지 수집 이동 본체"""

        def mo_xpath_injection(start: int) -> str:
            """google mobile xpath 경로 start는 a tag 기점 a -> a[2]"""
            if start == 2:
                return f'//*[@id="wepR4d"]/div/span/a'
            return f'//*[@id="wepR4d"]/div/span/a[{start-1}]'

        def pa_xpath_injection(start: int) -> str:
            """google site xpath 경로 start는 tr/td[3](page 2) ~ 기점"""
            return f'//*[@id="botstuff"]/div/div[3]/table/tbody/tr/td[{start}]/a'

        # 실행시작 지점
        self.driver.get(self.url)
        try:
            return self.a_loop_page(3, pa_xpath_injection)
        except NoSuchElementException:
            return self.a_loop_page(2, mo_xpath_injection)
        except WebDriverException as e:
            print(f"다음과 같은 이유로 google 수집 종료 --> {e}")
            self.driver.refresh()

    def search_box(self) -> UrlCollect:
        """수집 시작점
        - self.page_scroll_moving()
            - page 내리기
        - self.next_page_moving()
            - 다음 page 이동
        """
        self.driver.get(self.url)
        page_scroll_moving(self.driver, int(random.uniform(50, 100)))
        return self.next_page_moving()
