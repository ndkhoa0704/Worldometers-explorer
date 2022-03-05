from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time
import datetime


class Crawler:
    def __init__(self):
        # Get current date
        self._today = datetime.date.today()
        # Amount of time for a page to fully load
        self._SLEEP_TIME_FOR_ELEMENTS_EXPLICIT = 30
        # Amount of time for all elements in a page to fully load
        self._SLEEP_TIME_FOR_ELEMENTS_IMPLICIT = 0.5

    def _scroll_page(self, sleep_time, driver):
        # Continuously scoll to the end of the page
        # Configure sleep_time to wait for page loading
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(sleep_time)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _get_attributes(self, soup):
        attr = []
        attr_raw = soup.find_all(
            "th", attrs={"aria-controls": re.compile("main_table_countries_today")})
        for i in range(len(attr_raw)):
            attr.append(re.sub(
                ": .+", "", attr_raw[i]["aria-label"]).replace('\n', '').replace("&nbsp;", ' '))
        return attr

    def _get_instances(self, soup, day):
        instances = []
        # Select table to get correct data from 1 day
        table = soup.find("table", attrs={"id": f"main_table_countries_{day}"})
        rows = table.find_all(
            "tr", attrs={"role": "row", "class": ["odd", "even"]})
        # Remove summary on the first row
        rows.pop(0)
        # For each instance parse to get data
        for ins_raw in rows:
            tmp = []
            ins_r = ins_raw.find_all('td')
            if len(ins_r) == 0:
                continue
            ins_r.pop(0)
            if ins_r[0].string == None:
                continue
            tmp.append(ins_r[0].string.strip())
            for i in range(1, len(ins_r) - 2):
                if ins_r[i].string == None or len(ins_r[i].string.strip()) == 0:
                    tmp.append('N/A')
                else:
                    tmp.append(ins_r[i].string.strip().replace(',', ''))
            # Get poplulation
            if ins_r[-2].a != None:
                tmp.append(ins_r[-2].a.string.strip().replace(',', ''))
            else:
                tmp.append(ins_r[-2].string.strip().replace(',', ''))
            # Get continent
            if ins_r[-1].string == None or len(ins_r[-1].string.strip()) == 0:
                tmp.append('N/A')
            else:
                tmp.append(ins_r[-1].string.strip())
            instances.append(tmp)

        return instances

    def _save_file(self, filename, attrs, instances):
        with open(f"data/{filename}.tsv", "w") as f:
            f.write('\t'.join(attrs) + '\n')
            for i in instances:
                f.write('\t'.join(i) + '\n')

    def crawl(self):

        # Setup driver
        option = Options()
        option.add_argument('headless')
        option.add_argument('no_sandbox')
        option.add_argument('disable_gpu')
        driver = Chrome(service=Service('./chromedriver'), options=option)

        # 3 recent days
        day = [
            "today",
            "yesterday",
            "yesterday2"
        ]

        driver.get("https://www.worldometers.info/coronavirus/")

        # Scrolling and get page source
        self._scroll_page(self._SLEEP_TIME_FOR_ELEMENTS_IMPLICIT, driver)
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        attrs = self._get_attributes(soup)
        # Crawling
        for i in range(len(day)):
            driver.find_element(By.ID, f'nav-{day[i]}-tab')
            instances = self._get_instances(soup, day[i])
            date = self._today - datetime.timedelta(days=i)
            self._save_file(
                f"worldometers-{date.strftime('%Y-%m-%d')}", attrs, instances)

        driver.close()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.crawl()
