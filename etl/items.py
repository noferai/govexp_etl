from datetime import datetime as dt

import pydantic
import scrapy


class Organization(pydantic.BaseModel):
    url: pydantic.HttpUrl
    name: str
    inn: str
    kpp: str
    ogrn: str
    address: str


class ContactInfo(pydantic.BaseModel):
    person: str
    email: pydantic.EmailStr
    phone: str


class OrderItem(pydantic.BaseModel):
    reg_number: str
    url: pydantic.HttpUrl
    status: str
    obj: str
    employer: Organization
    contact: ContactInfo
    starting_price: float
    currency: str
    created: dt.date
    updated: dt.date
    end_date: dt.date


class ContractItem(scrapy.Item):
    pass


class AgreementItem(scrapy.Item):
    pass
