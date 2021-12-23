from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticPipeline:
    def __init__(self, es_host, es_port, es_user, es_pass):
        self.es_host = es_host
        self.es_port = es_port
        self.es_user = es_user
        self.es_pass = es_pass
        self.client = Elasticsearch(
            hosts=[{"host": self.es_host, "port": self.es_port, "use_ssl": True}],
            http_auth=(self.es_user, self.es_pass),
        )
        self.buffer = []

    def insert_items(self):
        items = self.buffer
        self.buffer = []
        bulk(self.client, items)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_host=crawler.settings.get("ES_HOST"),
            es_port=crawler.settings.get("ES_PORT"),
            es_user=crawler.settings.get("ES_USER"),
            es_pass=crawler.settings.get("ES_PASS"),
        )

    def close_spider(self, spider):
        self.insert_items()
        self.client.transport.close()


class ElasticInsertPipeline(ElasticPipeline):
    def __init__(self, es_host, es_port, es_user, es_pass):
        super().__init__(es_host, es_port, es_user, es_pass)

    def open_spider(self, spider):
        if not self.client.indices.exists(index=spider.es_index_id):
            self.client.indices.create(index=spider.es_index_id, body=spider.mapping)
            spider.logger.info(f"Index {spider.es_index_id} created")

    def process_item(self, item, spider):
        self.buffer.append({"_id": item.reg_number, "_index": spider.es_index_id, "_source": item.json()})
        if len(self.buffer) >= 100:
            self.insert_items()
        return item


class JsonPipeline:
    def process_item(self, item, spider):
        return item.json()
