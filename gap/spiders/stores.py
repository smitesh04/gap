import scrapy


class StoresSpider(scrapy.Spider):
    name = "stores"
    # allowed_domains = ["."]
    start_urls = ["https://www.gap.com/stores/sitemap.xml"]

    def parse(self, response, **kwargs):
        print()
