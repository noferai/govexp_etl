import json
import pathlib
from urllib import parse

import scrapy
from scrapy.http import HtmlResponse

from etl.settings import ROOT_DIR
from etl.spiders.base import BaseSpider
from etl.utils import add_domain


class AgreementSpider(BaseSpider):  # noqa
    es_index_id = "agreements"
    records_per_page = 50
    mapping = json.loads(pathlib.Path(f"{ROOT_DIR}/static/mappings/order.json").read_text())
    name = "AgreementSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/contractfz223/search/results.html"

    def push_documents(self, response: HtmlResponse):
        for document in response.xpath("//div[contains(@class, 'search-registry-entry-block')]"):
            url = add_domain(self.extract(document, ".//div[@class='registry-entry__header-mid__number']/a/@href"))
            reg_number = parse.parse_qs(parse.urlsplit(url).query).get("id")[0]  # noqa
            status = self.extract(document, ".//div[@class='registry-entry__header-mid__title']/text()")
            agreement = self.extract(document, ".//div[@class='registry-entry__body-value']/text()")
            organization_name = self.extract(document, ".//div[@class='registry-entry__body-href']/a/text()")
            organization_url = add_domain(self.extract(document, ".//div[@class='registry-entry__body-href']/a/@href"))

            price = self.extract(document, "//div[@class='price-block__value']/text()")
            dates = document.xpath(".//div[@class='data-block__value']/text()").getall()
            date, execution_period, created, updated = dates

            z = ""

            # yield scrapy.Request(
            #     url=url,
            #     callback=self.parse_notice,
            #     dont_filter=True,
            #     cb_kwargs=dict(
            #         url=url,
            #         status=status,
            #         reg_number=reg_number,
            #         agreement=agreement,
            #         notice_url=url,
            #         created=created,
            #         updated=updated,
            #         end_date=end_date,
            #         price=price,
            #         employer=dict(name=organization_name, url=organization_url),
            #     ),
            # )

    def parse_notice(self):
        ...

    def parse_employer(self):
        ...
