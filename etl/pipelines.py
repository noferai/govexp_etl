# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EtlPipeline:
    def process_item(self, item, spider):
        return item
