from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader


class DefaultLoader(ItemLoader):
    default_output_processor = TakeFirst()
