"""A pickle wrapper module with protocol=-1 by default."""

try:
    import cPickle as pickle  # PY2
except ImportError:
    import pickle


# 反序列化就是 将字符串 转换为 json数据
def loads(s):
    return pickle.loads(s)

# 序列化就是将json数据转换为字符串
def dumps(obj):
    return pickle.dumps(obj, protocol=-1)
