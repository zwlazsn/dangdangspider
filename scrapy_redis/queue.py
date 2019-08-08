from scrapy.utils.reqser import request_to_dict, request_from_dict

from . import picklecompat


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, server, spider, key, serializer=None):
        """Initialize per-spider redis queue.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        spider : Spider
            Scrapy spider instance.
        key: str
            Redis key where to put and get messages.
        serializer : object
            Serializer object with ``loads`` and ``dumps`` methods.

        """
        # 序列化 为None 则使用文件picklecompat
        if serializer is None:
            # Backward compatibility.
            # TODO: deprecate pickle.
            serializer = picklecompat
        # 当序列化文件 没有loads函数时 抛出异常
        # 抛出异常的目的 就是为了使传过来的序列化serializer 必须含有loads函数
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)
        # 下面的函数当前类的所有函数 都可以使用
        self.server = server
        self.spider = spider
        self.key = key % {'spider': spider.name}
        self.serializer = serializer
    # 将request进行编码为字符串
    def _encode_request(self, request):
        """Encode a request object"""
        # 将requests 转换为字典
        obj = request_to_dict(request, self.spider)
        # 将 字典转化为字符串进行返回
        return self.serializer.dumps(obj)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        # 将已经编码的encoded_request 解码为字典
        obj = self.serializer.loads(encoded_request)
        # 将dict转换为 request objects 可以直接通过下载器 进行下载
        return request_from_dict(obj, self.spider)

    # len方法 必须被重载 否则 不能使用
    # 返回一个队列的长度
    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    # 删除指定的键self.key
    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)

# first in first out 针对有序队列
class FifoQueue(Base):
    """Per-spider FIFO queue"""

    # 返回队列的长度
    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    # 从头部插入request
    def push(self, request):
        """Push a request"""
        # 编码request 插入self.key
        self.server.lpush(self.key, self._encode_request(request))

    # timeout 是超时 一般默认为0
    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            # 从尾部弹出一个元素
            data = self.server.rpop(self.key)
        if data:
            # 弹出的元素 再解码为request 直接给下载器下载
            return self._decode_request(data)


class PriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        # 使用的是 有序集合 实现优先级队列
        self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        # 实例化的函数  self.server 有一个方法叫做pipeline
        pipe = self.server.pipeline()
        pipe.multi()
        # zrange查询第一条数据 并返回 第一个元素  zremrangebyrank 删除第一个元素
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        # results 接收的是第一条数据 count删除的元素 返回的值 1 0
        results, count = pipe.execute()
        # 只要有一个元素 results就是真值
        if results:
            # 将获取到的第一个元素 拿出来 进行解码
            return self._decode_request(results[0])


class LifoQueue(Base):
    """Per-spider LIFO queue."""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


# TODO: Deprecate the use of these names.
SpiderQueue = FifoQueue
SpiderStack = LifoQueue
SpiderPriorityQueue = PriorityQueue
