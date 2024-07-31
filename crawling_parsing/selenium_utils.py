from typing import Any
from pathlib import Path

import urllib3
from urllib3 import exceptions
from urllib.parse import urlparse, urljoin

import re
import datetime
import time
import random


import pandas as pd
from bs4 import BeautifulSoup


import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent


urllib3.disable_warnings(exceptions.InsecureRequestWarning)


ua = UserAgent()


def chrome_option_injection() -> webdriver.Chrome:
    # 크롬 옵션 설정
    option_chrome = uc.ChromeOptions()
    option_chrome.add_argument("headless")
    option_chrome.add_argument("--disable-gpu")
    option_chrome.add_argument("--disable-infobars")
    option_chrome.add_argument("--disable-extensions")
    option_chrome.add_argument("--no-sandbox")
    option_chrome.add_argument("--disable-dev-shm-usage")
    option_chrome.add_argument(f"user-agent={ua.random}")

    caps = DesiredCapabilities().CHROME
    # page loading 없애기
    caps["pageLoadStrategy"] = "none"

    prefs = {
        "profile.default_content_setting_values": {
            "cookies": 2,
            "images": 2,
            "plugins": 2,
            "popups": 2,
            "geolocation": 2,
            "notifications": 2,
            "auto_select_certificate": 2,
            "fullscreen": 2,
            "mouselock": 2,
            "mixed_script": 2,
            "media_stream": 2,
            "media_stream_mic": 2,
            "media_stream_camera": 2,
            "protocol_handlers": 2,
            "ppapi_broker": 2,
            "automatic_downloads": 2,
            "midi_sysex": 2,
            "push_messaging": 2,
            "ssl_cert_decisions": 2,
            "metro_switch_to_desktop": 2,
            "protected_media_identifier": 2,
            "app_banner": 2,
            "site_engagement": 2,
            "durable_storage": 2,
        }
    }

    option_chrome.add_experimental_option("prefs", prefs)
    # webdriver_remote = webdriver.Remote(
    #     "http://chrome:4444/wd/hub", options=option_chrome
    # )
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService

    webdriver_remote = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=option_chrome
    )
    return webdriver_remote


def page_scroll_moving(
    driver: webdriver.Chrome, scroll1: int, scroll2: int = 30
) -> None:

    def scroll_page(scroll_cal: int, scroll: int, with_delay: bool) -> None:
        for i in range(int(scroll)):
            driver.execute_script(f"window.scrollTo(0, {i * scroll_cal})")
            if with_delay:
                time.sleep(1)

    prev_heigh = driver.execute_script("return document.body.scrollHeight")
    selected_scroll = random.choice([scroll1, scroll2])

    scroll_cal: float | int = prev_heigh / selected_scroll

    with_delay: bool = random.choice([True, False])

    scroll_page(scroll_cal, selected_scroll, with_delay)


path_location = Path(__file__).parent.parent.parent


def url_create(url: str) -> str:
    """URL 합성
    Args:
        url (str): url

    Returns:
        str: 완품 URL
            - ex) naver.com -> https://www.naver.com
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return f"https://{parsed_url.netloc or url}/"
    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def url_addition(base_url: str, url: str) -> str:
    """/~ 로 끝나는 URL을 붙여주는 함수
    Args:
        base_url (str): 기준 URL
        url (str): 추가할 URL

    Returns:
        str: 합쳐진 URL
    """
    if url.startswith("/"):
        return urljoin(url_create(base_url), url)
    return url


def href_from_text_preprocessing(text: str) -> str:
    """텍스트 전처리

    Args:
        text (str): URL title 및 시간
            - ex) 어쩌구 저쩌구...12시간

    Returns:
        str: 특수문자 및 시간제거
            - ex) 어쩌구 저쩌구
    """
    return re.sub(r"\b\d+시간 전\b|\.{2,}|[^\w\s]", "", text)


def time_extract(format: str) -> str:
    # 날짜와 시간 문자열을 datetime 객체로 변환
    date_obj = datetime.datetime.strptime(format, "%a, %d %b %Y %H:%M:%S %z")

    # 원하는 형식으로 변환
    formatted_date = date_obj.strftime("%Y-%m-%d: %H:%M:%S")
    return formatted_date


def href_from_a_tag(a_tag: BeautifulSoup, element: str = "href") -> str:
    """URL 뽑아내기

    Returns:
        str: [URL, ~~]
    """
    return a_tag.get(element)


def soup_data(
    html_data: str,
    element: str,
    elements: Any | None,
    soup: BeautifulSoup = None,
) -> list:
    """
    파싱 본체
    """
    if soup is None:
        soup = BeautifulSoup(html_data, "lxml")

    search_results = soup.find_all(element, elements)
    return search_results if search_results else []
