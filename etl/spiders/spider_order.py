from urllib import parse

import scrapy
from scrapy.http import HtmlResponse

from etl.spiders.base import BaseSpider
from etl.items import OrderItem, Organization, ContactInfo
from etl.utils import add_domain


class OrderSpider(BaseSpider):  # noqa
    name = "OrderSpider"
    url_to_parse = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"

    def push_documents(self, response: HtmlResponse):
        for document in response.xpath("//div[contains(@class, 'search-registry-entry-block')]"):
            url = add_domain(self.extract(document, ".//div[@class='registry-entry__header-mid__number']/a/@href"))
            reg_number = parse.parse_qs(parse.urlsplit(url).query).get("regNumber")[0]  # noqa
            status = self.extract(document, ".//div[@class='registry-entry__header-mid__title']/text()")
            obj = self.extract(document, ".//div[@class='registry-entry__body-value']/text()")
            organization_name = self.extract(document, ".//div[@class='registry-entry__body-href']/a/text()")
            organization_url = add_domain(self.extract(document, ".//div[@class='registry-entry__body-href']/a/@href"))

            starting_price = self.extract(document, "//div[@class='price-block__value']/text()")
            dates = document.xpath(".//div[@class='data-block__value']/text()").getall()
            try:
                created, updated, end_date = dates
            except ValueError:
                created, updated = dates
                end_date = None

            yield scrapy.Request(
                url=url,
                callback=self.parse_notice_new if "epz" in url else self.parse_notice_old,
                dont_filter=True,
                cb_kwargs=dict(
                    url=url,
                    status=status,
                    obj=obj,
                    reg_number=reg_number,
                    notice_url=url,
                    created=created,
                    updated=updated,
                    end_date=end_date,
                    starting_price=starting_price,
                    employer=dict(name=organization_name, url=organization_url),
                ),
            )

    def parse_notice_new(self, response: HtmlResponse, **kwargs):
        contact_selectors = response.xpath("//h2[contains(text(), 'Контактная информация')]/parent::div//section")
        contact_values = [
            key for key in map(str.strip, contact_selectors.xpath("string(span[2])").getall()) if len(key) > 0
        ]
        contact_keys = contact_selectors.xpath("string(span[1])").getall()
        contact = dict(zip(contact_keys, contact_values))

        yield scrapy.Request(
            url=kwargs["employer"]["url"],
            callback=self.parse_employer,
            dont_filter=True,
            cb_kwargs=dict(
                contact=ContactInfo(
                    person=contact.get("Ответственное должностное лицо"),
                    email=contact.get("Адрес электронной почты"),
                    phone=contact.get("Номер контактного телефона"),
                ),
                **kwargs,
            ),
        )

    def parse_notice_old(self, response: HtmlResponse, **kwargs):
        sections_dict = {}
        items = response.xpath("//div[contains(@class, 'noticeTabBoxWrapper')]//tr")

        for item in items:
            if (key := item.xpath("string(td[1])").get()) and (value := item.xpath("string(td[2])").get()):
                if len(key.strip()) > 0 and len(value.strip()) > 0:
                    sections_dict[key.strip()] = value.strip()

        yield scrapy.Request(
            url=kwargs["employer"]["url"],
            callback=self.parse_employer,
            dont_filter=True,
            cb_kwargs=dict(
                contact=ContactInfo(
                    person=sections_dict.get("Контактное лицо"),
                    email=sections_dict.get("Электронная почта"),
                    phone=sections_dict.get("Телефон"),
                ),
                **kwargs,
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
        yield OrderItem(employer=Organization(ogrn=ogrn, inn=inn, kpp=kpp, address=address, **employer_), **kwargs)
