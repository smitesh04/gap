import datetime
import os.path
import re
from typing import Iterable
import json
import scrapy
from scrapy import Request
from scrapy.cmdline import execute as ex
from gap.db_config import DbConfig
from gap.common_func import headers, create_md5_hash, page_write
from gap.items import GapItem


today_date = datetime.datetime.today().strftime("%d_%m_%Y")
obj = DbConfig()


class DataSpider(scrapy.Spider):
    name = "data"
    # allowed_domains = ["."]
    # start_urls = ["https://."]
    def start_requests(self):
        obj.cur.execute(f"select * from {obj.store_links_table} where status=0")
        rows = obj.cur.fetchall()
        for row in rows:
            link = row['link']
            link = link.replace("?cookieInitializationAttempted=true", "")

            hashid = create_md5_hash(link)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/gap/{today_date}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['hashid'] = hashid
            row['pagesave_dir'] = pagesave_dir
            row['file_name'] = file_name

            if os.path.exists(file_name):
                yield scrapy.Request(url='file:///'+file_name, callback=self.parse, cb_kwargs=row)
            else:
                yield scrapy.Request(url=link, headers=headers(), callback=self.parse, cb_kwargs=row)


    def parse(self, response, **kwargs):
        file_name = kwargs['file_name']
        pagesave_dir = kwargs['pagesave_dir']
        hashid = kwargs['hashid']
        if not os.path.exists(file_name):
            page_write(pagesave_dir, file_name, response.text)
        script_text = response.xpath("//script[@type='text/javascript' and contains(text(),'defaultData')]").get()
        script_text = script_text.replace(";</script>", "").replace('<script type="text/javascript">RLS.defaultData = ', '')
        script_text = script_text.strip()
        jsn = json.loads(script_text)

        lat = jsn['markerData'][0]['lat']
        lng = jsn['markerData'][0]['lng']

        info = jsn['markerData'][0]['info']
        info = info.replace('<div class="tlsmap_popup">', '').replace('</div>', '')

        info_jsn = json.loads(info)
        store_no = info_jsn['fid']
        country = info_jsn['country']
        store_name = info_jsn['location_name'].capitalize()
        street_address1 = info_jsn['address_1']
        street_address2 = info_jsn['address_2']
        if street_address2:
            street_address = street_address1+ street_address2
        else:
            street_address = street_address1
        region = info_jsn['region']
        postal_code = info_jsn['post_code']
        phone = info_jsn['local_phone']
        city = info_jsn['city']

        direction_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"

        open_hours_raw = response.xpath("//script[contains(text(), 'window.hours')]/text()").get()
        open_hours_text = re.findall('= {"label".*?}}};', open_hours_raw)[0]
        open_hours_text = open_hours_text.replace('= ', '').replace('}}};', '}}}')
        open_hours_jsn = json.loads(open_hours_text)

        try:
            days = open_hours_jsn['days']
            open_hours_list = list()
            for key, value in days.items():
                day = key
                close_time = value[0]['close']
                open_time = value[0]['open']
                open_hours_list.append(f'{day}: {open_time}-{close_time}')
            open_hours = ' | '.join(open_hours_list)
            status = "Open"
        except:
            open_hours = ''
            status = 'Closed'

        item = GapItem()
        item['store_no'] = store_no
        item['name'] = store_name
        item['latitude'] = lat
        item['longitude'] = lng
        item['street'] = street_address
        item['city'] = city
        item['state'] = region
        item['zip_code'] = postal_code
        item['county'] = city
        item['phone'] = phone
        item['open_hours'] = open_hours
        item['url'] = kwargs['link']
        item['provider'] = "Gap"
        item['category'] = "Apparel And Accessory Stores"
        item['updated_date'] = datetime.datetime.today().strftime("%d-%m-%Y")
        item['country'] = "US"
        item['status'] = status
        item['direction_url'] = direction_url
        item['pagesave_path'] = file_name
        yield item






if __name__ == '__main__':
    ex("scrapy crawl data".split())