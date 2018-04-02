import json
import hashlib


class Block(object):

    def __init__(self, data, index, timestamp, previous_hash, nonce, **kwargs):
        self.body = self.Body(data)
        self.head = self.Head(index, timestamp, previous_hash, nonce, **kwargs)

    @property
    def data(self):
        return self.body.data

    @property
    def nonce(self):
        return self.head.nonce

    @property
    def previous_hash(self):
        return self.head.previous_hash

    @property
    def index(self):
        return self.head.index

    def hash(self):
        block = json.dumps(self, sort_keys=True).encode()

        return hashlib.sha256(block).hexdigest()

    class Head(object):
        def __init__(self, index, timestamp, previous_hash, nonce, **kwargs):
            """

            :param index:
            :param timestamp:
            :param previous_hash:
            :param nonce: 随机数
            """
            if index == 0:
                # 创世块
                for k, v in kwargs.items():
                    self.__setattr__(k, v)

            self.index = index
            self.timestamp = timestamp
            self.previous_hash = previous_hash
            self.nonce = nonce

    class Body(object):
        def __init__(self, data):
            self.data = data