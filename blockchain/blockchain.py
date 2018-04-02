import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse

from .block import Block


class Blockchain(object):

    chain = []
    data = []
    nodes = set()  # 节点

    def __init__(self):
        pass
        # self.new_block(proof=100, previous_hash=1)

    def new_block(self, nonce):
        if len(self.chain) == 0:
            raise Exception('Can not new block as the genesis block dose not exist!')

        block = Block(
            data=self.data,
            index=len(self.chain) + 1,
            timestamp=time(),
            previous_hash=self.chain[-1].hash(),
            nonce=nonce
        )

        self.data = []

        self.chain.append(block)

        return self

    def generate_genesis_block(self):
        if len(self.chain) > 0:
            raise Exception('Can not generate genesis block as block already exist!')

        genesis_block = Block(
            data=[],
            index=0,
            timestamp=time(),
            previous_hash=None,
            nonce=0
        )

        self.chain.append(genesis_block)

        return self

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self):
        """
        寻找一个数 p，使得它与前一个区块的 nonce 拼接成的字符串的 Hash 值以 4 个零开头。
        :return:
        """
        nonce = 0
        while self.valid_proof(nonce) is False:
            nonce += 1

        return nonce

    def valid_proof(self, nonce, last_nonce=None):
        if last_nonce is None:
            last_nonce = self.last_block.nonce

        guess = f'{last_nonce}{nonce}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

        return self

    def valid_chain(self, chain):

        if len(chain) == 0 or len(chain) == 1:
            return True

        chain = iter(chain)

        last_block = next(chain)

        for block in chain:
            if block.previous_hash != last_block.hash():
                return False

            if not self.valid_proof(block.nonce, last_block.nonce):
                return False

            last_block = block

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes

        new_chain = self.chain

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                chain = response.json()

                if len(chain) > len(new_chain) and self.valid_chain(chain):
                    new_chain = chain

        self.chain = new_chain

        return self

    def new_transaction(self, timestamp, sender, recipient, amount):
        self.data.append({
            'timestamp': timestamp,
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block.index + 1

    def reward(self, recipient, amount=1):
        self.new_transaction(
            timestamp=time(),
            sender='0',
            recipient=recipient,
            amount=amount
        )

        return self
