from etl.constants import domain
import json


def add_domain(link: str):
    """Добавляет к ссылке протокол и домен"""
    if domain not in link and link[0] == "/":
        link = f"https://{domain}{link}"
    return link


def ascii_dumps(v, *, default):
    return json.dumps(v, default=default, ensure_ascii=False)
