from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from . import connection, defaults

# 序列化为字符串 默认的序列化函数
default_serialize = ScrapyJSONEncoder().encode


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue

    Settings
    --------
    REDIS_ITEMS_KEY : str
        Redis key where to store items.
    REDIS_ITEMS_SERIALIZER : str
        Object path to serializer function.

    """

    def __init__(self, server,
                 key=defaults.PIPELINE_KEY,
                 serialize_func=default_serialize):
        """Initialize pipeline.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        key : str
            Redis key where to store items.
        serialize_func : callable
            Items serializer function.

        """
        self.server = server
        self.key = key
        self.serialize = serialize_func

    # 将当前类传入函数
    # 用来生成参数和redis的连接实例
    @classmethod
    def from_settings(cls, settings):
        # from_settings = get_redis_from_settings
        # 生成redis连接实例
        params = {
            'server': connection.from_settings(settings),
        }
        # 如果设置里面有 item_key 我们就用设置中的

        if settings.get('REDIS_ITEMS_KEY'):
            params['key'] = settings['REDIS_ITEMS_KEY']
        # 如果设置中有序列化的函数 则优先使用设置中的

        if settings.get('REDIS_ITEMS_SERIALIZER'):
            params['serialize_func'] = load_object(
                settings['REDIS_ITEMS_SERIALIZER']
            )
        # 将参数初始化 给当前类
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    # 将item传递过来 自动触发这个函数 process_item
    def process_item(self, item, spider):
        # 创建一个线程 用于存储item 也就是说上一个item还没有存储完成
        # 下一个item就可以进行存储
        return deferToThread(self._process_item, item, spider)

    # 才是实现存储的函数
    def _process_item(self, item, spider):
        # 使用默认的序列化函数 将item序列化为字符串
        key = self.item_key(item, spider)
        data = self.serialize(item)
        # self.server 是redis的连接实例 rpush 右边插入一个元素

        self.server.rpush(key, data)
        return item
    # 生成一个item_key 用于存储item
    def item_key(self, item, spider):
        """Returns redis key based on given spider.

        Override this function to use a different key depending on the item
        and/or spider.

        """
        return self.key % {'spider': spider.name}
