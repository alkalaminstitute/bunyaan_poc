from datetime import datetime
import json
import requests
from Crypto.PublicKey import RSA
from urllib.parse import urlparse
from .Block import Block
from .Transaction import Transaction


class Blockchain:

    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []
        self.mining_reward = 10
        self.nodes = set()  # New

    def create_genesis_block(self):
        return Block("01/01/2022 8:90:23", "Genesis block")

    def get_last_block(self):
        return self.chain[-1]

    def mine_pending_txs(self, miner_address):

        # First reward the miner, should be done last
        self.pending_transactions.append(Transaction(
            None, miner_address, self.mining_reward))

        # If I successfully mine send reward to miningRewardAddress
        # In a real blockchain there are too many transactions to be put
        # in the same block so miners choose which transactions to include

        block = Block(
            datetime.now().strftime(
                "%m/%d/%Y, %H:%M:%S"),
            self.pending_transactions,
            self.get_last_block().hash
        )

        block.hash = block.calculate_hash()

        block.mine_block(self.difficulty)

        print("Block Successfully Mined")

        self.chain.append(block)

        # rewarding the miner in the next block
        # If the miner adds extra rewards other nodes in the network will ignore it
        self.pending_transactions = []

        return block

    def add_transaction(self, transaction):  # New
        if (not transaction.sender or not transaction.receiver):
            raise ValueError('Transacton must include from and to address')

        is_valid = transaction.is_valid_transaction()

        if (not is_valid):
            print("adsfadsfasdflasdfjlasdfljasdfl")
            print(transaction)
            raise ValueError('Cannot add invalid transaction to chain')

        self.pending_transactions.append(transaction)
        return "Transaction Added"

    def is_chain_valid(self, chain):
        # Check if the Genesis block hasn't been tampered with by comparing
        # the output of createGenesisBlock with the first block on our chain
        real_genesis = self.create_genesis_block().json_encode()

        if (real_genesis != self.chain[0].json_encode()):
            print("GNESIS IS NOT VALID")
            return False

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if (current_block.hash != current_block.calculate_hash()):
                print('curren is invalid')
                return False

            if (current_block.previous_hash != previous_block.hash):
                print(current_block.previous_hash)
                print(previous_block.hash)
                print('previous is invalid')
                return False

            # Check if all transactions in the current block are valid
            if (not current_block.has_valid_transactions()):
                print('has invalid transactions')
                return False

        return True

    def add_node(self, address):  # New
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):  # New
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        print(public_key.decode('ASCII'))
        return key.publickey().export_key().decode('ASCII')
