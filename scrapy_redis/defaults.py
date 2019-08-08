import redis


# For standalone use.
#去重的key
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'
# 定义的存储items的键名  spider是爬虫的名称
PIPELINE_KEY = '%(spider)s:items'
# reide的连接对象 用于连接redis
REDIS_CLS = redis.StrictRedis
# 字符集编码
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
# 连接redis的默认参数
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}
# 队列的变量名 用于存储爬取的url队列
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
# 优先级队列 用于规定队列的进出方法
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
# 用于去重的key  给requests加的指纹存储的地方
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'

# 用于生成指纹的类
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# 起始url对应key
START_URLS_KEY = '%(name)s:start_urls'
# 起始url的类型
START_URLS_AS_SET = False
