from scrapy.http import HtmlResponse

from etl.spiders.base import BaseSpider


class AgreementSpider(BaseSpider):  # noqa
    name = "AgreementSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/contractfz223/search/results.html"

    def parse_new(self, response: HtmlResponse, **kwargs):
        ...

    def parse_old(self, response: HtmlResponse, **kwargs):
        ...
