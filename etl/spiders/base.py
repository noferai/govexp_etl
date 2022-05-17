import unicodedata
from typing import Optional

import scrapy
from scrapy.http import HtmlResponse

from etl.constants import domain
from etl.utils import add_domain


class BaseSpider(scrapy.Spider):  # noqa
    name = "base"
    allowed_domains = [domain]
    records_per_page = 100
    url_to_parse = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def extract(response: HtmlResponse, query: str) -> Optional[str]:
        if (result := response.xpath(query).get()) is not None:
            return unicodedata.normalize("NFKD", result.strip())

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.url_to_parse}?pageNumber=1&recordsPerPage=_{self.records_per_page}",
            callback=self.push_pages,
            dont_filter=True,
        )

    def push_pages(self, response: HtmlResponse):
        pages_total = response.xpath("//ul[@class='pages']/li[last()]//span/text()").get()

        for page in range(1, int(pages_total) + 1):
            yield scrapy.Request(
                url=f"{self.url_to_parse}?pageNumber={page}&recordsPerPage=_{self.records_per_page}",
                callback=self.push_documents,
            )

    def push_documents(self, response: HtmlResponse):
        links_raw = response.xpath("//div[@class='registry-entry__header-mid__number']/a/@href").getall()
        links = list(map(add_domain, links_raw))

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_notice_new if "epz" in link else self.parse_notice_old)

    def parse_notice_new(self, response: HtmlResponse, **kwargs):
        """e.g. https://zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0119200000121016580"""
        ...

    def parse_notice_old(self, response: HtmlResponse, **kwargs):
        """e.g. https://zakupki.gov.ru/223/purchase/public/purchase/info/common-info.html?regNumber=32110938909"""
        ...
