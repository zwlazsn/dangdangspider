# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import  deepcopy
from urllib import parse
from dangdangspider.items import DangdangspiderItem

class DangdangSpider(RedisSpider):#scrapy.Spider
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key = "dangdang"
    def parse(self, response):
        #大分类
        div_list = response.xpath("//div[@class='con flq_body']/div")
        # print(response)
        # print(div_list)
        for div in div_list:
            # 实例化items
            item = DangdangspiderItem()
            # item = {}
            #大分类
            item['b_cate'] = div.xpath("./dl/dt//text()").extract()
            # print(item['b_cate'])
            item['b_cate'] = [i.strip() for i in item['b_cate'] if len(i.strip())>0]
            #有空值
            # print(item['b_cate'])
            #中间分组
            dl_list = div.xpath("./div//dl[@class='inner_dl']")
            for dl in dl_list:
                item['m_cate'] = dl.xpath("./dt//text()").extract()
                item['m_cate'] = [i.strip() for i in item['m_cate'] if len(i.strip())>0][0]
                # print(item['m_cate'])
                #小分类
                a_list= dl.xpath("./dd/a")
                for a in a_list:
                    item['a_href'] = a.xpath("./@href").extract()[0]
                    item['a_cate'] = a.xpath("./text()").extract()[0]

                    # print(item['a_href'],item['a_cate'])
                    if item['a_href'] is not None:
                        yield scrapy.Request(url=item['a_href'],callback=self.parse_book_list,
                                             meta={"item":deepcopy(item)})#不深拷贝 数据可能会重复


    def parse_book_list(self,response):
        item = response.meta["item"]
        li_list = response.xpath('//ul[@class="bigimg"]/li')
        for li in li_list:
            item["book_img"] = li.xpath('./a[@class="pic"]/img/@data-original | ./a[@class="pic"]/img/@src').extract_first()           # if "http://" not in item["book_img"]:
            item["book_name"] = li.xpath('./a/@title').extract()[0]
            # item["book_detail"] = li.xpath('./p[@class = "detail"]/text()').extract()[0]
            item["book_detail"] = li.xpath('./p[@class = "detail"]/text()').extract_first()

            item["book_price"] = li.xpath('./p[@class = "price"]/span[@class="search_now_price"]/text()').extract()[0]
            item["book_author"] = li.xpath('./p[@class ="search_book_author"]/span[1]/a[1]/@title').extract_first()
            item["book_publish_date"] = li.xpath('./p[@class ="search_book_author"]/span[2]/text()').extract_first()
            item["book_press"] = li.xpath('./p[@class ="search_book_author"]/span[3]/a[1]/@title').extract_first()
            item["book_url"] = li.xpath('./a/@href').extract()[0]
            # print(item["book_url"])
            # print(item)

        #next_url
        next_url = response.xpath("//li[@class ='next']/a/@href").extract_first()
        if next_url is not None:
            next_url = parse.urljoin(response.url,next_url)
            yield scrapy.Request(url=next_url,callback=self.parse_book_list,meta={"item":item})

        yield item