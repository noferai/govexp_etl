from scrapy.http import HtmlResponse
import json
import pathlib

from etl.spiders.base import BaseSpider
from etl.settings import ROOT_DIR


class AgreementSpider(BaseSpider):  # noqa
    es_index_id = "agreements"
    mapping = json.loads(pathlib.Path(f"{ROOT_DIR}/static/mappings/order.json").read_text())
    name = "AgreementSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/contractfz223/search/results.html"

    def parse_new(self, response: HtmlResponse, **kwargs):
        ...

    def parse_old(self, response: HtmlResponse, **kwargs):
        ...
