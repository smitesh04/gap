import scrapy
from scrapy.cmdline import execute as ex
import re
from gap.db_config import DbConfig

obj = DbConfig()



class StoresSpider(scrapy.Spider):
    name = "stores"
    # allowed_domains = ["."]
    start_urls = ["https://www.gap.com/stores/sitemap.xml"]

    def parse(self, response, **kwargs):
        links = re.findall('<loc>.*?</loc>', response.text)
        for link in links:
            store_link = link.replace("<loc>", "").replace("</loc>", "")
            if store_link.count("/") >= 6 and '.html' in store_link:
                obj.insert_store_links_table(store_link)





if __name__ == '__main__':
    ex("scrapy crawl stores".split())