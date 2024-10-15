# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from gap.db_config import DbConfig
from gap.items import GapItem

obj = DbConfig()

class GapPipeline:
    def process_item(self, item, spider):
        if isinstance(item, GapItem):

            obj.insert_data_table(item)
            obj.update_store_links_status(item['url'])


        return item
