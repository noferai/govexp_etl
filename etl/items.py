import datetime as dt
from typing import Optional, Union

import pydantic

from etl.utils import ascii_dumps


def to_dt(value: Optional[str]) -> Optional[dt.date]:
    if value is not None:
        try:
            date = dt.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            date = value
        return date


def parse_date(*fields: str) -> classmethod:
    decorator = pydantic.validator(*fields, allow_reuse=True, pre=True)
    validator = decorator(to_dt)
    return validator


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


class DatePeriod(pydantic.BaseModel):
    start: dt.date
    end: dt.date

    _start_end: classmethod = parse_date("start", "end")


class Item(pydantic.BaseModel):
    reg_number: str
    price: float
    url: pydantic.HttpUrl
    status: str | None
    employer: Organization
    created: dt.date
    updated: dt.date
    date: dt.date | None

    _dates: classmethod = parse_date("created", "updated", "date")

    class Config:
        json_dumps = ascii_dumps

    @pydantic.validator("price", pre=True)
    def parse_price(cls, value: str) -> float:
        return float(value[:-1].replace(" ", "").replace(",", "."))


class OrderItem(Item):
    obj: str
    contact: ContactInfo


class ContractItem(Item):
    contract: str
    execution_period: Union[DatePeriod, str]


class AgreementItem(Item):
    agreement: str
    execution_period: Union[DatePeriod, str]
