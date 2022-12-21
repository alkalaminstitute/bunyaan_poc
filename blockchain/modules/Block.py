import hashlib
import json
import jsonpickle
from Crypto.Signature import *


class Block (object):
    def __init__(self, timestamp, data, previous_hash=''):
        self.timestamp = timestamp
        self.data = data  # data since it may contain the special smartcontract txs
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):

        hashTransactions = ""

        hashString = str(self.timestamp) + str(len(self.data)) + \
            self.previous_hash + str(self.nonce)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def mine_block(self, difficulty):
        arr = []
        for i in range(0, difficulty):
            arr.append(i)

        # compute until the beginning of the hash = 0123..difficulty
        arrStr = map(str, arr)
        hashPuzzle = ''.join(arrStr)
        # print(len(hashPuzzle));
        while self.hash[0:difficulty] != hashPuzzle:
            self.nonce += 1
            self.hash = self.calculate_hash()
            # print(len(hashPuzzle));
            # print(self.hash[0:difficulty]);
        print("Block Mined!")
        return True

    def is_valid_block(self):

        if (self.hash != self.calculate_hash()):
            "Hash is invalid"
            return False

        if (not self.has_valid_transactions()):
            "Block has invalid transactions"
            return False

        return True

    def has_valid_transactions(self):
        for i in range(0, len(self.data)):
            transaction = self.data[i]
            if not transaction.is_valid_transaction():
                return False
        return True

    def json_encode(self):
        return jsonpickle.encode(self)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
