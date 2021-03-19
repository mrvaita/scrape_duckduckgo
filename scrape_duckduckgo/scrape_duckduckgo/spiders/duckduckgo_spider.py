from datetime import datetime
import scrapy
from bs4 import BeautifulSoup
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
import re


# Web Driver Options
browser_options = [
    "--ignore-certificate-errors", "--incognito", "--headless"
]


class DuckduckgoSpider(scrapy.Spider):
    name = "duckduckgo"
    base_url = "https://duckduckgo.com/?q={}"
    searches = [
        "mars+real+estate",
        "spotify+elon+musk",
        "spotify+elon+edm+musk",
    ]

    def __init__(self, name=None, **kwargs):
        super(DuckduckgoSpider, self).__init__(name, **kwargs)
        driver_options = webdriver.FirefoxOptions()
        for option in browser_options:
            driver_options.add_argument(option)
        self.driver = webdriver.Firefox(options=driver_options)

    @staticmethod
    def get_selenium_response(driver, url):
        driver.get(url)
        return driver.page_source.encode("utf-8")

    def start_requests(self):
        base_url = "https://duckduckgo.com/?q={}&t=h_&ia=web"
        searches = [
            "mars+real+estate",
            "spotify+elon+musk",
            "spotify+elon+edm+musk",
        ]
        for search in searches:
            url = base_url.format(search)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        search_title = response.url.split("?q=")[-1].replace("+", " ")
        search_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        soup = BeautifulSoup(
            self.get_selenium_response(self.driver, response.url),
            "html.parser"
        )

        search_results = soup.findAll(
            "div", attrs={"id": re.compile("r1-[0-2]")})
        
        search_results = [result.find(
            "a", attrs={re.compile("result__a")}) for result in search_results]
 
        with open("search_results.csv", "a") as f:
            for i, result in enumerate(search_results):
                result_link = re.search('href="(.+?)" rel', str(result)).group(1)
                result_name = result.get_text()
                f.write(";".join(
                    [search_title, result_name, result_link, str(i), search_time]) + "\n"
                )
