from scrapy.http import HtmlResponse

from etl.spiders.base import BaseSpider


class ContractSpider(BaseSpider):  # noqa
    name = "ContractSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/contract/search/results.html"

    def parse_new(self, response: HtmlResponse, **kwargs):
        ...

    def parse_old(self, response: HtmlResponse, **kwargs):
        ...
