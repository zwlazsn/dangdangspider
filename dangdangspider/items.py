# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 大分类
    b_cate = scrapy.Field()
    # 中间分类
    m_cate = scrapy.Field()
    #第三分类
    a_cate = scrapy.Field()
    a_href = scrapy.Field()
    #书的详细信息
    book_img = scrapy.Field()
    book_name = scrapy.Field()
    book_detail = scrapy.Field()
    book_price = scrapy.Field()
    book_author = scrapy.Field()
    book_publish_date = scrapy.Field()
    book_press = scrapy.Field()
    book_url = scrapy.Field()
