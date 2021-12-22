class ElasticSearchPipeline:
    def process_item(self, item, spider):
        return item


class JsonPipeline:
    def process_item(self, item, spider):
        return item.json(indent=1, ensure_ascii=False)
