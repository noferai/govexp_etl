import json
import pathlib
import re

import scrapy
from scrapy.http import HtmlResponse

from etl.items import AgreementItem, Organization, DatePeriod
from etl.settings import ROOT_DIR
from etl.spiders.base import BaseSpider
from etl.utils import add_domain


class AgreementSpider(BaseSpider):  # noqa
    es_index_id = "agreements_test"
    records_per_page = 50
    mapping = json.loads(pathlib.Path(f"{ROOT_DIR}/static/mappings/agreement.json").read_text())
    name = "AgreementSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/contractfz223/search/results.html"

    def push_documents(self, response: HtmlResponse):
        for document in response.xpath("//div[contains(@class, 'search-registry-entry-block')]"):
            url = add_domain(self.extract(document, ".//div[@class='registry-entry__header-mid__number']/a/@href"))
            reg_number = re.search(
                r"\d+", self.extract(document, ".//div[@class='registry-entry__header-mid__number']/a/text()")
            )[0]
            status = self.extract(document, ".//div[@class='registry-entry__header-mid__title']/text()")
            agreement = self.extract(document, ".//div[@class='registry-entry__body-value']/text()")
            organization_name = self.extract(document, ".//div[@class='registry-entry__body-href']/a/text()")
            organization_url = add_domain(self.extract(document, ".//div[@class='registry-entry__body-href']/a/@href"))

            price = self.extract(document, "//div[@class='price-block__value']/text()")
            dates = document.xpath(".//div[@class='data-block__value']/text()").getall()
            date, execution_period, created, updated = dates

            yield scrapy.Request(
                url=organization_url,
                callback=self.parse_employer,
                dont_filter=True,
                cb_kwargs=dict(
                    url=url,
                    status=status,
                    reg_number=reg_number,
                    agreement=agreement,
                    notice_url=url,
                    created=created,
                    updated=updated,
                    date=date,
                    execution_period=execution_period,
                    price=price,
                    employer=dict(name=organization_name, url=organization_url),
                ),
            )

    def parse_employer(self, response: HtmlResponse, **kwargs):
        """e.g. https://zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber=0119200000121016580"""
        info = response.xpath("//div[@class='registry-entry__body-block'][2]/div[@class='row']")

        ogrn = self.extract(info, "div[@class='col-md-auto'][1]/div[@class='registry-entry__body-value']/text()")
        inn = self.extract(info, "div[@class='col-md-auto'][2]/div[@class='registry-entry__body-value']/text()")
        kpp = self.extract(info, "div[@class='col-md-auto'][3]/div[@class='registry-entry__body-value']/text()")
        address = self.extract(info, "//div[@class='registry-entry__body-value']/text()")

        employer_ = kwargs.pop("employer")
        start_, _, end_ = kwargs.pop("execution_period").strip().split()
        yield AgreementItem(
            employer=Organization(ogrn=ogrn, inn=inn, kpp=kpp, address=address, **employer_),
            execution_period=DatePeriod(start=start_, end=end_),
            **kwargs,
        )
