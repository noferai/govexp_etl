from typing import Optional
import datetime as dt

import pydantic
import scrapy

from etl.utils import ascii_dumps


class Organization(pydantic.BaseModel):
    url: pydantic.HttpUrl
    name: str
    inn: str
    kpp: str
    ogrn: str
    address: str


class ContactInfo(pydantic.BaseModel):
    person: Optional[str]
    email: Optional[pydantic.EmailStr]
    phone: Optional[str]


class OrderItem(pydantic.BaseModel):
    reg_number: str
    url: pydantic.HttpUrl
    status: str
    obj: str
    employer: Organization
    contact: ContactInfo
    starting_price: float
    created: dt.date
    updated: dt.date
    end_date: Optional[dt.date]

    class Config:
        json_dumps = ascii_dumps

    @pydantic.root_validator(pre=True)
    def parse_price(cls, values: dict):
        values["starting_price"] = float(values["starting_price"][:-1].replace(" ", "").replace(",", "."))
        return values

    @pydantic.validator("created", "updated", "end_date", pre=True)
    def parse_date(cls, value: Optional[str]) -> Optional[dt.date]:
        if value is not None:
            return dt.datetime.strptime(value, "%d.%m.%Y").date()


class ContractItem(scrapy.Item):
    pass


class AgreementItem(scrapy.Item):
    pass
