from hashlib import sha256
import json
import time

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index # unique ID of the block
        self.transactions = transactions # list of transcations
        self.timestamp = timestamp # # time of generation of the block
        self.previous_hash = previous_hash # # hash of previous block
        self.nonce = nonce # 可以被不断添加，直至得到满足PoW（工作量证明）算法的hash

    # 计算block的hash
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self, chain=None):
        self.unconfirmed_transactions = [] #未经确认的事务池
        self.chain = chain # list of block
        if self.chain is None:
            self.chain = []
            self.create_genesis_block()


    # 创世区块（空）
    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    # 当前区块链中的最新（最末端）block
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        # previous block检查
        if previous_hash != block.previous_hash:
            raise ValueError("Previous hash incorrect")
       # 工作量检查
        if not Blockchain.is_valid_proof(block, proof):
            raise ValueError("Block proof invalid")

        block.hash = proof
        self.chain.append(block)

    @staticmethod
    def proof_of_work(block):
        """
        不断改变nonce值，以致满足工作量(blockchain.difficulty)
        （因为nonce也包含在block里，所以不断增加nonce可以使得computed_hash改变）
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    #添加到未被验证
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    # 检查hash、hash的工作量是否匹配
    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        # 对每一个block的hash和previous进行检查
        for block in chain:
            block_hash = block.hash

            # 需要删除hash属性以确保compute_hash的值一样
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        将未经验证的事务池打包成block，加入到当前的区块链
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True
