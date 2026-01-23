#!/usr/bin/python3
from conf.config_log import setup_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapy.http import TextResponse

import random, time
logger = setup_logger(__name__)


class ChromeDriver:
    """
    Selenium ChromeDriver 래퍼 클래스
    - Headless Chrome 실행
    - User-Agent 랜덤 적용
    - 자동 스크롤 지원
    """

    def __init__(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        ]

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--incognito")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-logging")
        options.add_argument(f"user-agent={random.choice(user_agents)}")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        logger.info("ChromeDriver 초기화 완료")

    def wait_css(self, element, timeout):
        """
        CSS Selector 기준 엘리먼트 로딩 대기
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, element))
            )
        except TimeoutException:
            logger.error(f"CSS 로딩 타임아웃: {element}")
            raise

    def autoscroll(self, element, timeout, sleep_sec, max_retry):
        """
        페이지 하단까지 자동 스크롤
        - height 변화 없을 경우 max_retry 후 중단
        """
        check_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        retry = 0

        logger.debug(f"[INIT] scrollHeight={check_height}")

        while True:
            time.sleep(sleep_sec)

            # 스크롤 다운
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            self.wait_css(element, timeout)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            logger.debug(f"[SCROLL] scrollHeight={new_height}")

            if new_height == check_height:
                retry += 1
                logger.debug(
                    f"[RETRY] height unchanged ({retry}/{max_retry})"
                )

                if retry == max_retry:
                    logger.info("스크롤 종료 (max_retry 도달)")
                    break
            else:
                check_height = new_height

    def __getattr__(self, name):
        """
        webdriver 메서드 위임
        """
        return getattr(self.driver, name)


class JobParser:
    """
    Selenium 페이지 소스를 Scrapy TextResponse로 변환 후
    채용 공고 헤더 데이터 추출
    """

    def __init__(self, browser):
        self.browser = browser
        self.response = None

    def get_response(self):
        """
        현재 페이지 HTML → Scrapy TextResponse 변환
        """
        self.response = TextResponse(
            url=self.browser.current_url,
            body=self.browser.page_source,
            encoding="utf-8"
        )
        logger.debug("Scrapy TextResponse 생성 완료")
        return self.response

    def get_job(
        self,
        domain,
        job_html,
        href_path,
        company_path,
        title_path
    ):
        """
        단일 채용 공고 HTML에서 데이터 추출
        return: {domain, href, company, title}
        """
        href = self.response.urljoin(
            job_html.xpath(href_path).get()
        )
        company = job_html.xpath(company_path).get()
        title = job_html.xpath(title_path).get()

        job_data = {
            "domain": domain,
            "href": href.strip(),
            "company": company.strip(),
            "title": title.strip()
        }

        return job_data
